import utils

search_context_name = "SearchContext"
mask_context_name = "MaskContext"
file_search_context_name = "FileSearchContext"
file_mask_context_name = "FileMaskContext"


def setup(session):
    model_url = utils.download_model('en-ner-person.bin', session)
    sent_url = utils.download_model('en-sent.bin', session)
    token_url = utils.download_model('en-token.bin', session)
    # Set up matchers to match on content of data here.
    search_context = {
        "name": search_context_name,
        "matchers": [
            {
                "name": "SsnMatcher",
                "type": "pattern",
                "pattern": r"\b(\d{3}[-]?\d{2}[-]?\d{4})\b"
            }
        ]
    }

    mask_context = {
        "name": mask_context_name,
        "rules": [
            {
                "name": "FpeRule",
                "type": "cosort",
                "expression": r"enc_fp_aes256_alphanum(${NAME})"
            },
            {
                "name": "RedactSsnRule",
                "type": "cosort",
                "expression": r"replace_chars(${SSN},'*',1,3,'*',5,2)"
            }
        ],
        "ruleMatchers": [
            {
                "name": "FpeRuleMatcher",
                "type": "name",
                "rule": "FpeRule",
                "pattern": "NameMatcher"
            },
            {
                "name": "SsnRuleMatcher",
                "type": "name",
                "rule": "RedactSsnRule",
                "pattern": "SsnMatcher"
            }
        ]
    }
# Set up JSON path matchers here. See 'NameMatcher' for an example of matching on any value associated with a key named 'name',
# regardless of position in JSON.
    file_search_context = {
        "name": file_search_context_name,
        "matchers": [
            {
                "name": search_context_name,
                "type": "searchContext"
            },
            {
                "name": "NameMatcher",
                "type": "jsonPath",
                "jsonPath": "$..name"
            },
        ]
    }

    file_mask_context = {
        "name": file_mask_context_name,
        "rules": [
            {
                "name": mask_context_name,
                "type": "maskContext"
            }
        ]
    }

    utils.create_context("searchContext", search_context, session)
    utils.create_context("maskContext", mask_context, session)
    utils.create_context("files/fileSearchContext", file_search_context, session)
    utils.create_context("files/fileMaskContext", file_mask_context, session)


def teardown(session):
    utils.destroy_context("searchContext", search_context_name, session)
    utils.destroy_context("maskContext", mask_context_name, session)
    utils.destroy_context("files/fileSearchContext", file_search_context_name, session)
    utils.destroy_context("files/fileMaskContext", file_mask_context_name, session)
