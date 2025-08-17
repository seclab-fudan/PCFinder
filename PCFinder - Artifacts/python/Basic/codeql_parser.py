#!/usr/bin/env python
# -*- coding: utf-8 -*-


# here put the import lib

import sys
import time

sys.path.append(".")
sys.path.append("..")

import json
from typing import Dict, List, Optional
import linecache
import os
import traceback

from Model.if_block import IFBlock
from Model.if_condition import IFCondition
from Model.if_method import IFMethod
from Model.if_true_block import IFTrueBlock
from Model.if_var import IFVar
from Basic.utils import *
from Basic.config import *

# if_loc -> {"method":[m1, m2], "var":[v1, v2], "path": [p1, p2], "path_var": [pv1, pv2], "path_method": [pm1, pm2]}
RESULT: Dict[str, Dict] = {}
# {cms: [{"method":"x", "var":"x"}, {"method":"x", "var":"x"}]}
SAVE_DICT = {}
USER_RELATED_DICT = {}
USER_RELATED_CLASS = []
IF_BLOCK_DICT = {}
OTHER_AUTH_DICT = {}
TAINT_AUTH_DICT = {}

GROUND_TRUTH = json.load(open("./Input/auth_if.json", "r"))


def parse_sarif_message(content: str, message_type: str):
    """parse message

    Args:
        content (str):
        message_type (str):
    """
    json_content: Dict = json.loads(content)
    results: List[Dict] = json_content["runs"][0]["results"]
    for result in results:
        parse_message_util(result["locations"][0]["physicalLocation"], result["message"]["text"], message_type)


def parse_all_if_cond(cms):
    """
    Args:
        cms (string):
    """
    content = get_if_content_sarif(cms)
    parse_sarif_message(content, IF_CONTENT_SUFFIX)
    content = get_if_cond_var_method_sarif(cms)
    parse_sarif_message(content, IF_COND_VAR_METHOD_SUFFIX)
    content = get_if_cond_control_sarif(cms)
    parse_sarif_message(content, IF_COND_CONTROL_VAR_SUFFIX)


def parse_message_util(locations, name, cond_type):
    """Parse the CodeQL file with message format, and save the result in the RESULT global variable.

    Args:
        locations (Dict): the location in sarif
        name (string):
        cond_type (string): message type
    """
    pass


def parse_if_true(cms):
    """parse if-true block

    Args:
        cms (string):
    """
    content = get_if_true_throw_sarif(cms)
    parse_sarif_message(content, IF_TRUE_THROW_SUFFIX)
    content = get_if_true_return_sarif(cms)
    parse_sarif_message(content, IF_TRUE_RETURN_SUFFIX)
    content = get_if_true_redirect_sarif(cms)
    parse_sarif_message(content, IF_TRUE_REDIRECT_SUFFIX)
    content = get_if_true_sso_sarif(cms)
    parse_sarif_message(content, IF_TRUE_SSO_SUFFIX)


def get_dict_by_type(result, types: str):
    res = {}
    if result.get(types):
        for i in result[types]:
            if types in ["if_cond_obj_method"]:
                name, params, param_type = i.split(":")
                res[name] = {"params": params, "ret_type": param_type}
            elif types in ["if_equals"]:
                for eq in i.split(CRLF):
                    var, is_mapper = eq.split(":")
                    if is_mapper == "1":
                        res[var] = True
                    else:
                        res[var] = False
            else:
                raise Exception(f"Types {types} not found")
        return res
    else:
        return None


def get_content_by_type(result, types: str) -> Optional[List]:
    res = []
    if result.get(types):
        for i in result[types]:
            res.append(i)
    return res


def get_content_by_loc(loc: str) -> str:
    content = ""
    file_loc, start_line, _, end_line, _ = loc.replace("file://", "").split(":")
    for i in range(int(start_line), int(end_line)):
        content += linecache.getline(file_loc, int(i)).strip() + "\n"
    content += linecache.getline(file_loc, int(end_line)).strip()
    return content


def get_content_by_loc_with_column(loc: str) -> str:
    content = ""
    file_loc, start_line, start_column, end_line, end_column = loc.replace("file://", "").split(":")
    if start_line == end_line:
        content = linecache.getline(file_loc, int(start_line))[int(start_column) - 1:int(end_column)].strip()
    else:
        content = linecache.getline(file_loc, int(start_line))[int(start_column) - 1:].strip() + "\n"
        for i in range(int(start_line) + 1, int(end_line)):
            content += linecache.getline(file_loc, int(i)).strip() + "\n"
        content += linecache.getline(file_loc, int(end_line))[:int(end_column)].strip()
    return content


def get_file_content_by_type(result, types: str) -> Optional[List]:
    res = set()
    if result.get(types):
        for loc in result[types]:
            content = get_content_by_loc(loc)
            res.add(content)
        return list(res)
    else:
        return None


def get_boolean_result(result, types: str) -> bool:
    boolean = result.get(types)
    if boolean == ["1"]:
        return True
    return False


def parse_json_to_obj(cms) -> List[IFBlock]:
    if_block_list_inner = []
    cms_src_path = f"{SRC_PATH}/{cms}/"

    for if_loc, result in RESULT.items():
        if_file, start_line, end_line = if_loc.split(":")
        if_file_path = os.path.join(cms_src_path, if_file)

        if_condition_stmt = ""
        for i in range(int(start_line), int(end_line) + 1):
            if_condition_stmt += linecache.getline(if_file_path, int(i)).strip()

        # init if_block
        if_block = IFBlock(cms, if_loc)
        if_block.conditions_content = if_condition_stmt

        # get the result of if block
        if_content = ""
        if_position = ""
        method_name = ""
        block_range = result.get(IF_CONTENT_SUFFIX)
        if block_range:
            start_line, start_column, end_line, end_column, if_position, method_name = block_range[0].split(SEP)
            if_content += linecache.getline(if_file_path, int(start_line))[int(start_column) - 1:].strip() + "\n"
            for i in range(int(start_line) + 1, int(end_line)):
                if_content += linecache.getline(if_file_path, int(i)).strip() + "\n"
            if_content += linecache.getline(if_file_path, int(end_line))[:int(end_column)].strip()
        if_block.content = if_content
        if_block.if_position = if_position
        if_block.method_name = method_name

        # controllable
        if_control_var_dict = {}
        if_control_var = get_content_by_type(result, IF_COND_CONTROL_VAR_SUFFIX)
        for var in if_control_var:
            source, sink = var.split(DOT)
            if sink not in if_control_var_dict.keys():
                if_control_var_dict[sink] = [source]
            else:
                if_control_var_dict[sink].append(source)

        # if condition
        if_condition_list = []
        if_block.conditions = if_condition_list

        if_cond_var_methods = get_content_by_type(result, IF_COND_VAR_METHOD_SUFFIX)
        for cond in if_cond_var_methods:
            if_var_list = []
            if_method_list = []
            if_condition = IFCondition(cms, if_loc)
            # split if cond
            if_condition_loc, var, method, getter = cond.split(SEP)
            if_condition.content = get_content_by_loc_with_column(if_condition_loc)
            if getter != "":
                if_condition.getter = getter.split(DOT)
            for vv in var.split(DOT):
                if vv != "":
                    vv_name, vv_type, vv_loc = vv.split(SPLIT)
                    user_related = None
                    if_var = IFVar(cms, if_condition_loc, vv_name, vv_type)
                    if_var.is_user_related = user_related
                    if vv_name in if_control_var_dict.keys():
                        if_var.source = if_control_var_dict[vv_name]
                        if_var.is_control = 1
                    if_var_list.append(if_var)
            for mm in method.split(DOT):
                if mm != "":
                    mm_name, mm_type = mm.split(":")
                    if_method = IFMethod(cms, if_condition_loc, mm_name, mm_type)
                    if_method_list.append(if_method)
            if_condition.vars = if_var_list
            if_condition.methods = if_method_list
            if_condition.if_block = if_block
            if_condition_list.append(if_condition)

        # if true block
        if_true_block = IFTrueBlock(cms, if_loc)
        if_block.true_block = if_true_block

        # interrupt / sso
        if_true_sso = get_content_by_type(result, IF_TRUE_SSO_SUFFIX)
        if_true_return = get_content_by_type(result, IF_TRUE_RETURN_SUFFIX)
        if_true_throw = get_content_by_type(result, IF_TRUE_THROW_SUFFIX)
        if_true_redirect = get_content_by_type(result, IF_TRUE_REDIRECT_SUFFIX)

        if len(if_true_sso) != 0:
            if_true_block.type.append("SSO")
            if_true_block.sso_content = if_true_sso
        if if_true_return:
            if_true_block.type.append("Return")
            if_return_result, if_str, if_var, if_method, if_const = if_true_return[0].split(SEP)
            if_return_loc, return_method_name, return_type = if_return_result.split(SPLIT)
            if_true_block.interrupt_content.append(get_content_by_loc(if_return_loc))
            if_true_block.interrupt_info["return"] = {
                "if_str": if_str,
                "if_var": if_var,
                "if_method": if_method,
                "if_const": if_const
            }
            if_block.wrapper_method = return_method_name
            if_block.wrapper_return_type = return_type
        if if_true_throw:
            if_true_block.type.append("Throw")
            if_throw_result, if_throw, if_str, if_var, if_method, if_const = if_true_throw[0].split(SEP)
            if_throw_loc, return_method_name, return_type = if_throw_result.split(SPLIT)

            if_true_block.interrupt_content.append(get_content_by_loc(if_throw_loc))
            if_true_block.interrupt_info["throw"] = {
                "if_throw": if_throw,
                "if_str": if_str,
                "if_var": if_var,
                "if_method": if_method,
                "if_const": if_const
            }
            if_block.wrapper_method = return_method_name
            if_block.wrapper_return_type = return_type
        if if_true_redirect:
            if_true_block.type.append("Redirect")
            if_redirect_result, if_str, if_var, if_method, if_const = if_true_redirect[0].split(SEP)
            if_redirect_loc, return_method_name, return_type = if_redirect_result.split(SPLIT)

            if_true_block.interrupt_content.append(get_content_by_loc(if_redirect_loc))
            if_true_block.interrupt_info["redirect"] = {
                "if_str": if_str,
                "if_var": if_var,
                "if_method": if_method,
                "if_const": if_const
            }
            if_block.wrapper_method = return_method_name
            if_block.wrapper_return_type = return_type

        if_block_list_inner.append(if_block)
    return if_block_list_inner


def parse_json_to_obj_dict(cms) -> Dict[str, IFBlock]:
    if_block_list_inner = {}
    cms_src_path = f"{SRC_PATH}/{cms}/"

    for if_loc, result in RESULT.items():
        if_file, start_line, end_line = if_loc.split(":")
        if_file_path = os.path.join(cms_src_path, if_file)

        if_condition_stmt = ""
        for i in range(int(start_line), int(end_line) + 1):
            if_condition_stmt += linecache.getline(if_file_path, int(i)).strip()

        if_block = IFBlock(cms, if_loc)
        if_block.conditions_content = if_condition_stmt

        if_content = ""
        if_position = ""
        method_name = ""
        block_range = result.get(IF_CONTENT_SUFFIX)
        if block_range:
            start_line, start_column, end_line, end_column, if_position, method_name = block_range[0].split(SEP)
            if_content += linecache.getline(if_file_path, int(start_line))[int(start_column) - 1:].strip() + "\n"
            for i in range(int(start_line) + 1, int(end_line)):
                if_content += linecache.getline(if_file_path, int(i)).strip() + "\n"
            if_content += linecache.getline(if_file_path, int(end_line))[:int(end_column)].strip()
        if_block.content = if_content
        if_block.if_position = if_position
        if_block.method_name = method_name

        if_control_var_dict = {}
        if_control_var = get_content_by_type(result, IF_COND_CONTROL_VAR_SUFFIX)
        for var in if_control_var:
            source, sink = var.split(DOT)
            if sink not in if_control_var_dict.keys():
                if_control_var_dict[sink] = [source]
            else:
                if_control_var_dict[sink].append(source)

        if_condition_list = []
        if_block.conditions = if_condition_list

        if_cond_var_methods = get_content_by_type(result, IF_COND_VAR_METHOD_SUFFIX)
        for cond in if_cond_var_methods:
            if_var_list = []
            if_method_list = []
            if_condition = IFCondition(cms, if_loc)
            if_condition_loc, var, method, getter = cond.split(SEP)
            if_condition.content = get_content_by_loc_with_column(if_condition_loc)
            if getter != "":
                if_condition.getter = getter.split(DOT)
            for vv in var.split(DOT):
                if vv != "":
                    vv_name, vv_type, vv_loc = vv.split(SPLIT)
                    user_related = None
                    if_var = IFVar(cms, if_condition_loc, vv_name, vv_type)
                    if_var.is_user_related = user_related
                    if vv_name in if_control_var_dict.keys():
                        if_var.source = if_control_var_dict[vv_name]
                        if_var.is_control = 1
                    if_var_list.append(if_var)
            for mm in method.split(DOT):
                if mm != "":
                    mm_name, mm_type = mm.split(":")
                    if_method = IFMethod(cms, if_condition_loc, mm_name, mm_type)
                    if_method_list.append(if_method)
            if_condition.vars = if_var_list
            if_condition.methods = if_method_list
            if_condition.if_block = if_block
            if_condition_list.append(if_condition)

        if_true_block = IFTrueBlock(cms, if_loc)
        if_block.true_block = if_true_block

        if_true_sso = get_content_by_type(result, IF_TRUE_SSO_SUFFIX)
        if_true_return = get_content_by_type(result, IF_TRUE_RETURN_SUFFIX)
        if_true_throw = get_content_by_type(result, IF_TRUE_THROW_SUFFIX)
        if_true_redirect = get_content_by_type(result, IF_TRUE_REDIRECT_SUFFIX)

        if len(if_true_sso) != 0:
            if_true_block.type.append("SSO")
            if_true_block.sso_content = if_true_sso
        if if_true_return:
            if_true_block.type.append("Return")
            if_return_result, if_str, if_var, if_method, if_const = if_true_return[0].split(SEP)
            if_return_loc, return_method_name, return_type = if_return_result.split(SPLIT)
            if_true_block.interrupt_content.append(get_content_by_loc(if_return_loc))
            if_true_block.interrupt_info["return"] = {
                "if_str": if_str,
                "if_var": if_var,
                "if_method": if_method,
                "if_const": if_const
            }
            if_block.wrapper_method = return_method_name
            if_block.wrapper_return_type = return_type
        if if_true_throw:
            if_true_block.type.append("Throw")
            if_throw_result, if_throw, if_str, if_var, if_method, if_const = if_true_throw[0].split(SEP)
            if_throw_loc, return_method_name, return_type = if_throw_result.split(SPLIT)
            if_true_block.interrupt_content.append(get_content_by_loc(if_throw_loc))
            if_true_block.interrupt_info["throw"] = {
                "if_throw": if_throw,
                "if_str": if_str,
                "if_var": if_var,
                "if_method": if_method,
                "if_const": if_const
            }
            if_block.wrapper_method = return_method_name
            if_block.wrapper_return_type = return_type
        if if_true_redirect:
            if_true_block.type.append("Redirect")
            if_redirect_result, if_str, if_var, if_method, if_const = if_true_redirect[0].split(SEP)
            if_redirect_loc, return_method_name, return_type = if_redirect_result.split(SPLIT)
            if_true_block.interrupt_content.append(get_content_by_loc(if_redirect_loc))
            if_true_block.interrupt_info["redirect"] = {
                "if_str": if_str,
                "if_var": if_var,
                "if_method": if_method,
                "if_const": if_const
            }
            if_block.wrapper_method = return_method_name
            if_block.wrapper_return_type = return_type

        if_block_list_inner[if_loc] = if_block
    return if_block_list_inner


def parse_sarif_without_if_message(content: str) -> List:
    messages = []
    return messages


def is_user_related_var(cms, var_loc) -> bool:
    if var_loc in USER_RELATED_DICT[cms]:
        return True
    return False


def is_user_related_var_loose(var) -> bool:
    if var in USER_RELATED_CLASS:
        return True
    return False


def get_all_extended_class() -> Dict:
    all_extended_class_dict = {}
    for cms in DBS:
        content = get_all_user_related_extended_class_sarif(cms)
        all_class_result = parse_sarif_without_if_message(content)
        class_dict = {}
        for ii in all_class_result:
            for i in ii.split("\n"):
                source_class_name, sink_var_name, sink_var_type, _ = i.split(SPLIT)
                single_dict = {sink_var_name: sink_var_type}
                if source_class_name not in class_dict.keys():
                    class_dict[source_class_name] = [single_dict]
                else:
                    if single_dict not in class_dict[source_class_name]:
                        class_dict[source_class_name].append(single_dict)
                if cms not in all_extended_class_dict.keys():
                    all_extended_class_dict[cms] = [class_dict]
                else:
                    if class_dict not in all_extended_class_dict[cms]:
                        all_extended_class_dict[cms].append(class_dict)
    return all_extended_class_dict


def get_all_extended_class_by_cms(cms) -> Dict:
    all_extended_class_dict = {}
    content = get_all_user_related_extended_class_sarif(cms)
    all_class_result = parse_sarif_without_if_message(content)
    class_dict = {}
    for ii in all_class_result:
        for i in ii.split("\n"):
            source_class_name, sink_var_name, sink_var_type, _ = i.split(SPLIT)
            single_dict = {sink_var_name: sink_var_type}
            if source_class_name not in class_dict.keys():
                class_dict[source_class_name] = [single_dict]
            else:
                if single_dict not in class_dict[source_class_name]:
                    class_dict[source_class_name].append(single_dict)
            if cms not in all_extended_class_dict.keys():
                all_extended_class_dict[cms] = [class_dict]
            else:
                if class_dict not in all_extended_class_dict[cms]:
                    all_extended_class_dict[cms].append(class_dict)
    return all_extended_class_dict


def init_all_user_related_extended_var():
    for cms in DBS:
        USER_RELATED_DICT[cms] = []
        content = get_all_user_related_extended_class_sarif(cms)
        all_class_result = parse_sarif_without_if_message(content)
        for ii in all_class_result:
            for i in ii.split("\n"):
                source_class_name, sink_var_name, sink_var_type, sink_var_loc = i.split(SPLIT)
                USER_RELATED_DICT[cms].append(sink_var_loc)


def init_user_related_class():
    d = json.load(open("./Cache/all_user_related_class_dict.json", "r"))
    for i, v in d.items():
        for ii in v:
            USER_RELATED_CLASS.append(ii["name"])
    return USER_RELATED_CLASS


def init_user_related_class_with_taint_obj(cms):
    user_related_class_obj = []
    d = json.load(open("./Cache/all_user_related_class_dict_taint.json", "r"))
    for ii in d[cms]:
        user_related_class_obj.append(ii)
    return user_related_class_obj


def get_all_class():
    all_class_dict = {}
    for cms in DBS:
        content = get_all_class_sarif(cms)
        all_class_result = parse_sarif_without_if_message(content)
        for i in all_class_result:
            class_name, super_class, instance, fields, methods = i.split(SPLIT)
            class_dict = {
                "name": class_name,
                "superclass": [],
                "objs": [],
                "fields": [],
                "methods": [],
            }
            for s in super_class.split(DOT):
                if not s:
                    continue
                class_dict["superclass"].append(s)
            for o in instance.split(DOT):
                if not o:
                    continue
                class_dict["objs"].append(o)
            for f in fields.split(DOT):
                if not f:
                    continue
                modifier, type_, name, = f.split(SEP)
                field_dict = {
                    "name": name,
                    "type": type_,
                    "modifier": modifier,
                    "class_name": class_name,
                }
                class_dict["fields"].append(field_dict)
            for m in methods.split(DOT):
                if not m:
                    continue
                modifier, type_, name, = m.split(SEP)
                method_dict = {
                    "name": name,
                    "type": type_,
                    "modifier": modifier,
                }
                class_dict["methods"].append(method_dict)
            if cms not in all_class_dict.keys():
                all_class_dict[cms] = [class_dict]
            else:
                all_class_dict[cms].append(class_dict)
    return all_class_dict


def get_all_class_by_cms(cms):
    all_class_dict = {}
    content = get_all_class_sarif(cms)
    all_class_result = parse_sarif_without_if_message(content)
    for i in all_class_result:
        class_name, super_class, instance, fields, methods = i.split(SPLIT)
        class_dict = {
            "name": class_name,
            "superclass": [],
            "objs": [],
            "fields": [],
            "methods": [],
        }
        for s in super_class.split(DOT):
            if not s:
                continue
            class_dict["superclass"].append(s)
        for o in instance.split(DOT):
            if not o:
                continue
            class_dict["objs"].append(o)
        for f in fields.split(DOT):
            if not f:
                continue
            modifier, type_, name, = f.split(SEP)
            field_dict = {
                "name": name,
                "type": type_,
                "modifier": modifier,
            }
            class_dict["fields"].append(field_dict)
        for m in methods.split(DOT):
            if not m:
                continue
            modifier, type_, name, = m.split(SEP)
            method_dict = {
                "name": name,
                "type": type_,
                "modifier": modifier,
            }
            class_dict["methods"].append(method_dict)
        if cms not in all_class_dict.keys():
            all_class_dict[cms] = [class_dict]
        else:
            all_class_dict[cms].append(class_dict)
    return all_class_dict


def get_if_object() -> List[IFBlock]:
    if_block_list = []
    for cms in DBS:
        try:
            parse_all_if_cond(cms)
            parse_if_true(cms)
            if_block_list.extend(parse_json_to_obj(cms))
        except Exception as e:
            traceback.print_exc()
            logger.error(f"[-]Error at {cms}: {str(e)}")
        RESULT.clear()
    return if_block_list


def init_if_object():
    for cms in DBS:
        IF_BLOCK_DICT[cms] = []
        try:
            parse_all_if_cond(cms)
            parse_if_true(cms)
            IF_BLOCK_DICT[cms].extend(parse_json_to_obj(cms))
        except Exception as e:
            traceback.print_exc()
            logger.error(f"[-]Error at {cms}: {str(e)}")
        RESULT.clear()


def get_if_object_dict_by_cms(cms) -> Dict[str, IFBlock]:
    if_block_dict = {}
    init_all_user_related_extended_var()
    init_user_related_class()
    try:
        parse_all_if_cond(cms)
        parse_if_true(cms)
        if_block_dict = parse_json_to_obj_dict(cms)
    except Exception as e:
        traceback.print_exc()
        logger.error(f"[-]Error at {cms}: {str(e)}")
    RESULT.clear()
    return if_block_dict


def get_if_object_by_cms(cms) -> List[IFBlock]:
    if not IF_BLOCK_DICT:
        init_if_object()
    return IF_BLOCK_DICT[cms]


def init_auth_dict():
    for cms in DBS:
        OTHER_AUTH_DICT[cms] = set()
        content = get_other_credentials_sarif(cms)
        json_content: Dict = json.loads(content)
        results: List[Dict] = json_content["runs"][0]["results"]
        for result in results:
            credentials = result["message"]["text"]
            OTHER_AUTH_DICT[cms].add(credentials)


def get_other_auth_fields(cms) -> List[str]:
    if not OTHER_AUTH_DICT:
        init_auth_dict()
    return OTHER_AUTH_DICT[cms]


def get_tainted_auth_fields(cms):
    if not TAINT_AUTH_DICT:
        init_taint_auth_dict()
    return TAINT_AUTH_DICT[cms]

def init_taint_auth_dict():
    for cms in DBS:
        TAINT_AUTH_DICT[cms] = set()
        content = get_all_user_related_extended_class_sarif(cms)
        json_content: Dict = json.loads(content)
        results: List[Dict] = json_content["runs"][0]["results"]
        for result in results:
            credentials = result["message"]["text"]
            TAINT_AUTH_DICT[cms].add(credentials)


def main():
    get_if_object()

    a = get_all_class()
    with open("./Input/all_class_dict.json", "w") as ff:
        json.dump(a, ff)

    # a = get_all_extended_class()
    # with open(f"{INPUT_PREFIX}/all_extended_class_dict.json", "w") as ff:
    #     json.dump(a, ff)
    # print(json.dumps(get_all_class()))

if __name__ == "__main__":
    main()
