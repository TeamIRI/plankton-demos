# DarkShield Files API: DICOM Search/Masking

## Synopsis

This example demonstrates the use of the *darkshield-files* API to search and mask
*DICOM* (.dcm) files and the associated CSV metadata within a directory that emulates a DICOM filesystem.

Everything in the filesystem will be sent to be searched and masked, including folder names.

The output will be placed into a separate directory.

## Details

DICOM files contain a list of attributes that include information about the scan/image such as patient name and hospital, along with the pixel data of the scan.

Typically, most sensitive data in a DICOM file is contained in attributes separate to the pixel data itself.

These separate attributes are typically overlayed onto the view of the scan when viewing with a DICOM viewer.

However, in this demo, a certain DICOM file in the filesystem is known to contain burned-in text containing the patient's name in the top left corner of the pixel data itself, in addition to the sensitive
information in the attributes.

For this file, a separate file mask content is set up to define the coordinates of a black box to redact this burned-in text.

## Requirements

At least version 1.3.0 of the DarkShield API is required to run this demo.

To run, the *plankton* web services API must be hosted at 
the location specified in *server_config.py* (by default *http://localhost:8959*) with both the *darkshield* and *darkshield-files* 
plugins installed.

## Search Matchers and Masking Rules

The example will search and mask the following with format-preserving encryption:
1. Credit cards (with a regular expression pattern, validated by a JavaScript file)
2. Dates (with a regular expression pattern)
3. Emails (with a regular expression pattern)
4. IP addresses (with a regular expression pattern)
5. First names (with a set file, ignoring case, and only taking complete matches)
6. Last names (with a set file, ignoring case, and only taking complete matches)
7. Names as a whole (with a named entity recognition model)
8. Phone numbers (with a regular expression pattern)
9. Social security numbers (with a regular expression pattern)
10. URLs (with a regular expression pattern)
11. ZIP codes (with a regular expression pattern)
12. Vehicle identification numbers (with a regular expression pattern, validated by a JavaScript file)

## Execution

To execute, run `python main.py`.

The results of the masked filesystem will be placed inside of the *masked* directory in the same structure the original was in.
