#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

# here put the import lib
import yaml
from pathlib import Path
import logging

from Basic.config import *


def get_src_path(cms):
    content = Path(f"{DB_PATH}/{cms}/codeql-database.yml").read_bytes()
    return yaml.load(content, Loader=yaml.Loader)["sourceLocationPrefix"]


def get_src_path_sql(cms):
    content = Path(f"{DB_PATH}/{cms}/codeql-database.yml").read_bytes()
    return yaml.load(content, Loader=yaml.Loader)["sourceLocationPrefix"]


# all if
def get_if_content_sarif(cms) -> str:
    return Path(f"{IF_CONTENT_SARIF_PATH}/{cms}_{IF_CONTENT_SUFFIX}.sarif").read_text()


def get_if_cond_var_method_sarif(cms) -> str:
    return Path(f"{IF_COND_VAR_METHOD_SARIF_PATH}/{cms}_{IF_COND_VAR_METHOD_SUFFIX}.sarif").read_text()


def get_if_cond_control_sarif(cms) -> str:
    return Path(f"{IF_COND_CONTROL_VAR_SARIF_PATH}/{cms}_{IF_COND_CONTROL_VAR_SUFFIX}.sarif").read_text()


def get_other_credentials_sarif(cms) -> str:
    return Path(f"{CREDENTIALS_SARIF_PATH}/{cms}_{CREDENTIALS_SUFFIX}.sarif").read_text()


# if true
def get_if_true_throw_sarif(cms) -> str:
    return Path(f"{IF_TRUE_THROW_SARIF_PATH}/{cms}_{IF_TRUE_THROW_SUFFIX}.sarif").read_text()


def get_if_true_return_sarif(cms) -> str:
    return Path(f"{IF_TRUE_RETURN_SARIF_PATH}/{cms}_{IF_TRUE_RETURN_SUFFIX}.sarif").read_text()


def get_if_true_redirect_sarif(cms) -> str:
    return Path(f"{IF_TRUE_REDIRECT_SARIF_PATH}/{cms}_{IF_TRUE_REDIRECT_SUFFIX}.sarif").read_text()


def get_if_true_sso_sarif(cms) -> str:
    return Path(f"{IF_TRUE_SSO_SARIF_PATH}/{cms}_{IF_TRUE_SSO_SUFFIX}.sarif").read_text()


def get_all_class_sarif(cms) -> str:
    return Path(f"{ALL_CLASS_SARIF_PATH}/{cms}_{ALL_CLASS_SUFFIX}.sarif").read_text()


def get_all_extended_class_sarif(cms) -> str:
    return Path(f"{ALL_CLASS_EXTENDED_SARIF_PATH}/{cms}_{ALL_CLASS_EXTENDED_SUFFIX}.sarif").read_text()


def get_all_user_related_extended_class_sarif(cms) -> str:
    return Path(f"{USER_RELATED_EXTENDED_SARIF_PATH}/{cms}_{USER_RELATED_EXTENDED_SUFFIX}.sarif").read_text()


def get_logger():
    logger = logging.getLogger(__file__)
    logger.setLevel(logging.DEBUG)

    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)

    log_path = Path(Path(__file__).resolve().parent / "log")
    if not log_path.is_dir():
        log_path.mkdir(parents=True, exist_ok=True)

    fh = logging.FileHandler(log_path / 'log.txt', mode="w")
    fh.setLevel(logging.DEBUG)

    logger.addHandler(sh)
    logger.addHandler(fh)
    return logger


logger = get_logger()
