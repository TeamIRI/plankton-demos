import utils

search_context_name = "SearchContext"
mask_context_name = "MaskContext"
file_search_context_name = "FileSearchContext"
file_mask_context_name = "FileMaskContext"


def setup(session):
    search_context = {
        "name": search_context_name,
        "matchers": [
            {
                "name": "NameMatcher",
                "type": "transformer",
                "entityLabels": ["PER"]
            },
            {
                "name": "EmailMatcher",
                "type": "pattern",
                "pattern": r"\b[\w._%+-]+@[\w.-]+\.[A-Za-z]{2,4}\b"
            }
        ]
    }

    mask_context = {
        "name": mask_context_name,
        "rules": [
            {
                "name": "FpeRule",
                "type": "cosort",
                "expression": "enc_fp_aes256_alphanum($\{INPUT\})"
            }
        ],
        "ruleMatchers": [
            {
                "name": "FpeRuleMatcher",
                "type": "name",
                "rule": "FpeRule",
                "pattern": "NameMatcher|EmailMatcher|ColumnMatcher"
            }
        ]
    }

    file_search_context = {
        "name": file_search_context_name,
        "matchers": [
            {
                "name": search_context_name,
                "type": "searchContext"
            }
            ,
            {
                "name": "ColumnMatcher",
                "type": "column",
                "pattern": "NK1|4"
            }
             ,
            {
                "name": "ColumnMatcher",
                "type": "column",
                "pattern": "OBX|2"
            }
             ,
            {
                "name": "ColumnMatcher",
                "type": "column",
                "pattern": "OBX|3"
            }
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
