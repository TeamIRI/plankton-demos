import json
import logging
import ntpath
import os
import sys
from tkinter.filedialog import askopenfilename

import requests

# Append parent directory to PYTHON_PATH so we can import utils.py
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from setup import setup, teardown, file_mask_context_name, file_search_context_name
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import FileTarget
from utils import base_url

if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    s = requests.Session()
    try:
        setup(s)
        url = f'{base_url}/files/fileSearchContext.mask'
        context = json.dumps({
            "fileSearchContextName": file_search_context_name,
            "fileMaskContextName": file_mask_context_name
        })
        os.makedirs('masked', exist_ok=True)
        while True:
            filename = askopenfilename()
            if not filename:
                break
            basename = ntpath.basename(filename)
            process_files = [(filename, 'masked')]
            for file_name, masked_folder in process_files:
                files = {'file': open(file_name, 'rb'), 'context': context}
                logging.info(f"POST: sending '{file_name}' to {url}")
                with s.post(url, files=files, stream=True) as r:
                    if r.status_code >= 300:
                        logging.info(f"Failed with status {r.status_code}:\n\n{r.json()}")
                        break

                    logging.info(
                        f"Extracting 'masked_{basename}' and 'masked_{basename}_results.json' into {masked_folder}.")
                    parser = StreamingFormDataParser(headers=r.headers)
                    parser.register('file', FileTarget(f'{masked_folder}/masked_{basename}'))
                    parser.register('results', FileTarget(f'{masked_folder}/masked_{basename}_results.json'))
                    for chunk in r.iter_content(4096):
                        parser.data_received(chunk)
    finally:
        teardown(s)
