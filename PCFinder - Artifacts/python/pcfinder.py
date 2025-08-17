#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from typing import Set

from Basic.codeql_parser import *
from AuthIF.analysis import get_credentials
import pandas as pd


permission_check = {}

def show_all_cases(lst, _type):
    for if_block in lst:
        print(_type)
        print(if_block.cms, if_block.loc)
        print(if_block.conditions_content)
        print(if_block.content)
        print(f"{if_block.is_auth_permission_check_by_user()} - {if_block.is_auth_permission_check_by_interrupt()}")
        print('\n')


def res_evaluate(if_block_list):
    _fn, _fp, _tn, _tp = 0, 0, 0, 0
    for if_block in if_block_list:
        if if_block.tool_res and if_block.gt:
            _tp += 1
        elif if_block.tool_res and not if_block.gt:
            _fp += 1
        elif not if_block.tool_res and if_block.gt:
            _fn += 1
        elif not if_block.tool_res and not if_block.gt:
            _tn += 1
    print(f"{if_block_list[0].cms} FN: {_fn} FP: {_fp} TP: {_tp}")


def get_method_gt(cms) -> List:
    auth_method = []
    if_block_obj_list = get_if_object_by_cms(cms)
    for if_block in if_block_obj_list:
        if if_block.gt and if_block.if_position == "method":
            auth_method.append(if_block.method_name)
    auth_method = list(set(auth_method))
    return auth_method


def if_block_filter(cms, mode) -> List[IFBlock]:
    if_block_obj_list = get_if_object_by_cms(cms)
    filter_if_block_list = []
    for if_block in if_block_obj_list:
        if mode == "contextunware":
            filter_if_block_list.append(if_block)
            continue
        if not if_block.true_block.has_sso() and not if_block.true_block.has_interrupt() and not if_block.is_in_interceptor():
            continue
        filter_if_block_list.append(if_block)
    return filter_if_block_list


def normalize(cond: IFCondition) -> str:
    condition = cond.content
    # normalize vars (to type)
    for var in cond.vars:
        if var.type != "String":
            condition = condition.replace(var.name, var.type)
    for i in [" ", "\n"]:
        condition = condition.replace(i, "")
    for i in ["!=", "==", ">=", "<=", ">", "<"]:
        condition = condition.replace(i, "[OP]")
    return condition


def if_condition_cluster(if_block_list: List[IFBlock]) -> Dict[str, List[IFCondition]]:
    cluster_dict = {}
    print(len(if_block_list))
    for if_block in if_block_list:
        for cond in if_block.conditions:
            if not cond.is_contain_user_related_vars() and not if_block.is_in_interceptor():
                continue
            condition = normalize(cond)
            if condition in cluster_dict.keys():
                cluster_dict[condition].append(cond)
            else:
                cluster_dict[condition] = [cond]
    return cluster_dict


def show(cluster: Dict[str, List[IFCondition]]):
    for k, v in cluster.items():
        if len(v) < 2:
            continue
        print(f"====={k}=====")
        for if_block in v:
            if_block = if_block.if_block
            print(if_block.gt)
            print(if_block.loc)
            print(if_block.conditions_content)
            print(if_block.content)
            print("\n")


def get_precision_gt():
    import pandas as pd
    result_dict = {}
    # df = pd.read_excel("./Input/precision.xlsx", sheet_name='pcif_precision_all')
    # selected_columns = ["cms", "location", "type"]
    # selected_data = df[selected_columns]
    # for index, row in selected_data.iterrows():
    #     result_dict[row['cms'] + row["location"]] = row["type"]

    # df = pd.read_excel("./Input/precision.xlsx", sheet_name='pcif_precision_all_0830')
    # selected_columns = ["cms", "location", "type"]
    # selected_data = df[selected_columns]
    # for index, row in selected_data.iterrows():
    #     result_dict[row['cms'] + row["location"]] = row["type"]

    # df = pd.read_excel("./Input/precision.xlsx", sheet_name='pcif_precision_all_1026')
    # selected_columns = ["cms", "location", "type"]
    # selected_data = df[selected_columns]
    # for index, row in selected_data.iterrows():
    #     result_dict[row['cms'] + row["location"]] = row["type"]

    df = pd.read_excel("./Input/precision.xlsx", sheet_name='all_cms_res')
    selected_columns = ["cms", "location", "type"]
    selected_data = df[selected_columns]
    for index, row in selected_data.iterrows():
        result_dict[row['cms'] + row["location"]] = row["type"]

    return result_dict


def evaluate_result(cms, res):
    tp = 0
    result_dict = get_precision_gt()
    tp_l: List[IFBlock] = []
    for loc, if_condition in permission_check.items():
        if_block = if_condition.if_block
        tp_l.append(if_block)
    print(f"{len(tp_l)}")
    for if_block in tp_l:
        _r = [result_dict[if_block.cms + if_block.loc] if (if_block.cms + if_block.loc) in result_dict.keys() else 'UNKNOWN' ,
              if_block.cms,
              if_block.loc,
              if_block.conditions_content + '\n' + if_block.content,
            ]
        res.append(_r)


def evaluate_result_filter(filter_list: List, res):
    for if_block in filter_list:
        _r = [if_block.gt,
              if_block.cms,
              if_block.loc,
              if_block.conditions_content + '\n' + if_block.content,
              f"{if_block.is_auth_permission_check_by_interrupt()}"]
        res.append(_r)


def find_permission_check_by_feature(if_block_obj_list: List[IFBlock], field_access_method, mode):
    for if_block in if_block_obj_list:
        for cond in if_block.conditions:
            if (
                    if_block.is_auth_permission_check_by_interrupt()
            ) or (
                    cond.is_auth_condition_constant()
            ):
                permission_check[cond.loc] = cond

        for cond in if_block.conditions:
            if if_block.true_block.check_body_by_keyword():
                continue
            for i in cond.getter:
                clazz, _method, _field = i.split(".")
                if f"{clazz}.{_field}" in field_access_method:
                    for var in cond.vars:
                        if mode == "contextunware":
                            if var.type == clazz:
                                permission_check[cond.loc] = cond
                        else:
                            if var.type == clazz and not var.is_control:
                                permission_check[cond.loc] = cond
                    for method in cond.methods:
                        if method.package == clazz and method.name_body == _method:
                            for var in cond.vars:
                                if mode == "contextunware":
                                    if var.type == method.package:
                                        permission_check[cond.loc] = cond
                                else:
                                    if var.type == method.package and not var.is_control:
                                        permission_check[cond.loc] = cond


def get_user_field(if_block_obj_list: List[IFBlock], cms) -> List:
    """
    :param if_block_obj_list:
    :param cms:
    :return:
    """
    field_access_method = set()
    user_related_class = init_user_related_class_with_taint_obj()
    for block in if_block_obj_list:
        for cond in block.conditions:
            if block.is_auth_permission_check_by_interrupt() or cond.is_auth_condition_constant():
                if len(cond.getter):
                    for i in cond.getter:
                        clazz = i.split(".")[0]
                        if i.split(".")[0] in user_related_class:
                            for var in cond.vars:
                                if var.type == clazz and not var.is_control:
                                    field_access_method.add(i)
                for i in cond.vars:
                    if "." in i.name and i.name.islower() and not i.is_control:
                        clazz = i.type
                        field = i.name.split(".")[1]
                        method = f"get{field[:1].upper()}{field[1:]}"
                        if clazz in user_related_class:
                            field_access_method.add(f"{clazz}.{method}.{field}")
    return list(field_access_method)


def is_in_if(cms, match_class_field: List):
    result = set()
    if_block_obj_list = if_block_filter(cms)
    for block in if_block_obj_list:
        for cond in block.conditions:
            for i in cond.getter:
                if i in match_class_field:
                    clazz = i.split(".")[0]
                    for var in cond.vars:
                        if var.type == clazz and not var.is_control:
                            result.add(i)
            for var in cond.vars:
                if "." in var.name and var.name.islower() and not var.is_control:
                    clazz = var.type
                    field = var.name.split(".")[1]
                    method = f"get{field[:1].upper()}{field[1:]}"
                    tmp = f"{clazz}.{method}.{field}"
                    if tmp in match_class_field:
                        result.add(tmp)
    return list(result)


def get_class_count(clazz: Set):
    result = set()
    for i in clazz:
        result.add(i.split(".")[0])
    return len(result)


def get_permission_check_dict(cms) -> Dict:
    pc_dict = {}
    credentials = get_credentials()
    in_if_field = []
    for c in credentials[cms]:
        for f in c['authentication_credentials']:
            in_if_field.append(f"{c['name']}.{f['name']}")
        for f in c['authorization_credentials']:
            in_if_field.append(f"{c['name']}.{f['name']}")

    filtered_if_block_obj_list = if_block_filter(cms, mode="1")
    find_permission_check_by_feature(filtered_if_block_obj_list, in_if_field, mode="1")

    pc_block = []
    for loc, if_condition in permission_check.items():
        if_block = if_condition.if_block
        pc_block.append(if_block)
    for if_block in pc_block:
        pc_dict[if_block.loc] = if_block

    permission_check.clear()
    return pc_dict


def main():
    res = [['type', 'cms', 'location', 'content', 'tag']]
    mode = ""
    if len(sys.argv) > 1 and sys.argv[1] == "cu":
        mode = "contextunware"
    credentials = get_credentials()
    for cms in DBS:
        filtered_if_block_obj_list = if_block_filter(cms, mode)
        in_if_field = []
        for c in credentials[cms]:
            for f in c['authentication_credentials']:
                in_if_field.append(f"{c['name']}.{f['name']}")
            for f in c['authorization_credentials']:
                in_if_field.append(f"{c['name']}.{f['name']}")
        find_permission_check_by_feature(filtered_if_block_obj_list, in_if_field, mode)
        evaluate_result(cms, res)
        permission_check.clear()
    pd.DataFrame(res).to_csv("./Cache/all_cms_res.csv", encoding="UTF-8", header=False, index=False)



if __name__ == "__main__":
    main()










