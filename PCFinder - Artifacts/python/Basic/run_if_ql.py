#!/usr/bin/env python
# -*- coding: utf-8 -*-

# here put the import lib
import sys
sys.path.append(".")
sys.path.append("..")

import pathlib
import os
from Basic.config import *
from concurrent.futures import ThreadPoolExecutor
import queue
from typing import List
import threading
import time
from utils import logger
import re

TASK = [
    ## Preprocessing
    # if content
    f"code/if_content.ql:{IF_CONTENT_SARIF_PATH}/{{}}_{IF_CONTENT_SUFFIX}.sarif",
    # if condition
    f"code/if_cond_var_method.ql:{IF_COND_VAR_METHOD_SARIF_PATH}/{{}}_{IF_COND_VAR_METHOD_SUFFIX}.sarif",
    # all class
    f"code/all_class.ql:{ALL_CLASS_SARIF_PATH}/{{}}_{ALL_CLASS_SUFFIX}.sarif",

    # ## Credential Candidates Inferring
    # credentials in others
    f"code/credentials.ql:{CREDENTIALS_SARIF_PATH}/{{}}_{CREDENTIALS_SUFFIX}.sarif",
    # # controllable analysis
    f"pdg/source_to_if_control_pdg.ql:{IF_COND_CONTROL_VAR_SARIF_PATH}/{{}}_{IF_COND_CONTROL_VAR_SUFFIX}.sarif",
    f"code/extended_user_related_class.ql:{USER_RELATED_EXTENDED_SARIF_PATH}/{{}}_{USER_RELATED_EXTENDED_SUFFIX}.sarif",

    ### Permission Check Identification
    f"cfg/if_true_sso.ql:{IF_TRUE_SSO_SARIF_PATH}/{{}}_{IF_TRUE_SSO_SUFFIX}.sarif",
    f"cfg/if_return.ql:{IF_TRUE_RETURN_SARIF_PATH}/{{}}_{IF_TRUE_RETURN_SUFFIX}.sarif",
    f"cfg/if_throw.ql:{IF_TRUE_THROW_SARIF_PATH}/{{}}_{IF_TRUE_THROW_SUFFIX}.sarif",
    f"cfg/if_redirect.ql:{IF_TRUE_REDIRECT_SARIF_PATH}/{{}}_{IF_TRUE_REDIRECT_SUFFIX}.sarif",
    
    # ## utility evaluation
    # f"utility/path_pdg.ql:{UTILITY_PDG_PATH}/{{}}_{IF_COND_CONTROL_VAR_SUFFIX}.sarif",

    # --------------
    # if count
    # f"code/if_count.ql:{IF_COUNT_SARIF_PATH}/{{}}_count.sarif"
]

pool = ThreadPoolExecutor(RUN_QL_THREAD_NUM)
q = queue.Queue()
lock = threading.RLock()
lock_cms = {}


def multithread_codeql():
    while not q.empty():
        command = q.get()
        pool.submit(run_codeql, command)


def provider(cmss):
    """publish task
    """
    if not cmss:
        cmss = DBS
    for t in TASK:
        for cms in cmss:
            lock_cms[cms] = 1
            task_args = t.format(cms)
            task_ql, task_output = task_args.split(":")
            output_dir = os.path.dirname(task_output)
            pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)
            command = f"codeql database analyze --rerun {DB_PATH}/{cms} {QL_PATH}/{task_ql} --max-paths=2 --threads={CODEQL_THREAD_NUM} --ram={CODEQL_RAM} --format=sarif-latest --output={task_output} --warnings=hide"
            q.put([command, cms])

def run_codeql(args: List):
    """subscribe task

    Args:
        args (List): command + cmsname
    """
    command = args[0]
    cms = args[1]

    lock.acquire()
    while not lock_cms[cms]:
        time.sleep(1)
        logger.debug(f"Waiting lock {cms}")
        continue
    lock_cms[cms] = 0
    lock.release()

    start = time.time()

    os.system(command)
    lock_cms[cms] = 1

    end = time.time()
    ql = re.findall('[\w]+\.ql', command)[0]
    logger.info(f"[+]{ql} on {cms} cost {int(end - start)} Seconds")


if __name__ == "__main__":
    start = time.time()
    if len(sys.argv) > 1:
        provider([sys.argv[1]])
    else:
        provider(None)
    multithread_codeql()
    pool.shutdown()
    end = time.time()
    logger.info(f"[+]Cost {end - start} Seconds")
    logger.info(f"{end - start}")
    