import argparse
import json
import logging
import os
import sys

import requests
from google.cloud import storage

# Append parent directory to PYTHON_PATH so we can import utils.py
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from requests_toolbelt import MultipartEncoder
from setup import setup, teardown, file_mask_context_name, file_search_context_name
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget, FileTarget
from utils import base_url

if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    session = requests.Session()
    parser = argparse.ArgumentParser(description='Demo for GCP bucket search/masking.')
    parser.add_argument('masked_bucket_name', type=str, help="The destination for masked blobs.")
    parser.add_argument('bucket_name', type=str, help="The name of the bucket to be searched.")
    parser.add_argument('folder_name_or_file_path', nargs='?', type=str, default='',
                        help="Prefix e.g.(folder1/folder2/) or full path to file folder/example.txt.")
    args = parser.parse_args()
    masked_bucket_name = args.masked_bucket_name
    bucket_name = args.bucket_name
    folder_prefix = args.folder_name_or_file_path
    if folder_prefix != '':
        if folder_prefix.find('/') == -1 and folder_prefix.find('.') == -1:
            logging.info("Folder name or file path was not in correct format (folder/ or folder/example.txt)")
            exit()

    client = storage.Client()
    bucket = client.bucket(bucket_name)

    masked_bucket = client.bucket(masked_bucket_name)
    masked_bucket.storage_class = "STANDARD"
    if not masked_bucket.exists():
        masked_bucket = client.create_bucket(masked_bucket, location="us")

    try:
        setup(session)
        url = f'{base_url}/files/fileSearchContext.mask'
        context = json.dumps({
            "fileSearchContextName": file_search_context_name,
            "fileMaskContextName": file_mask_context_name
        })

        for blob in bucket.list_blobs(prefix=folder_prefix):
            # For larger files, a streaming solution should be used so that the file isn't loaded
            # fully in memory before being sent to the API.
            if not blob.name.endswith("/"):
                content = blob.download_as_bytes()
                process_files = [(blob.name, blob.content_type)]

                for file_name, media_type in process_files:
                    f = content
                    encoder = MultipartEncoder(fields={
                        'context': ('context', context, 'application/json'),
                        'file': (file_name, f, media_type)
                    })
                    folder_name = f"results/{file_name.replace('.', '_')}"
                    os.makedirs(folder_name, exist_ok=True)
                    logging.info(f"POST: sending '{file_name}' to {url}")
                    with session.post(url, data=encoder, stream=True,
                                      headers={'Content-Type': encoder.content_type}) as r:
                        if r.status_code >= 300:
                            raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")
                        logging.info(f"Extracting '{file_name}' and 'results.json' into {folder_name}.")
                        parser = StreamingFormDataParser(headers=r.headers)
                        masked_file = ValueTarget()
                        parser.register('file', masked_file)
                        parser.register('results', FileTarget(f'{folder_name}/results.json'))
                        for chunk in r.iter_content(4096):
                            parser.data_received(chunk)
                        destination = blob.name
                        logging.info(f"putting masked file in '{destination}'.")
                        destination = masked_bucket.blob(destination)
                        destination.upload_from_string(masked_file.value, blob.content_type)

    finally:
        teardown(session)
