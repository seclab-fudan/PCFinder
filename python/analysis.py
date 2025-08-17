#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import pandas as pd

from Basic.codeql_parser import *
from utils import find_user_credentials_by_frequency

logging.basicConfig(level=logging.INFO)

BASE_CLASS = ['int', 'integer', 'string', 'long', 'short', 'boolean', "char"]

USER_FIELDS = {}

def load_json(filepath) -> Dict:
    return json.loads(open(filepath, 'rb').read().decode('utf-8'))


def find_no_user_class_cms(all_user_class_dict):
    for cms in all_user_class_dict:
        if not all_user_class_dict[cms]:
            print(cms)


def get_all_user_class_num(all_user_class_dict):
    num = 0
    for cms in all_user_class_dict:
        num += len(all_user_class_dict[cms])
    return num


def get_all_user_field_num(all_user_class_dict):
    res = 0
    for cms in all_user_class_dict:
        num = [len(c['fields']) for c in all_user_class_dict[cms]]
        res += sum(num)
    print(res)
    return res

def show_all_fields(cms, name, fields):
    if not fields:
        return
    print(cms)
    print(name)
    for field in fields:
        print(field['modifier'], field['type'], field['name'])
    print('\n')


def show_all_methods(cms, name, methods):
    if not methods:
        return
    print(cms)
    print(name)
    for method in methods:
        print(method['modifier'], method['type'], method['name'])
    print('\n')


def extract_cms_user_class_name(all_user_class_dict) -> Dict:
    res = {}
    for cms, user_class_dict in all_user_class_dict.items():
        res[cms] = set([i['name'] for i in user_class_dict if len(i["authentication_credentials"]) or len(i["authorization_credentials"])])
    return res


def extract_cms_authentication_credentials_name(all_user_class_dict) -> Dict:
    count = 0
    res = {}
    for cms, user_class_dict in all_user_class_dict.items():
        res[cms] = set([f"{i['name']}.{c['name']}" for i in user_class_dict for c in i['authentication_credentials']])
        count += len(res[cms])
    print(f"Authentication credentials: {count}")
    return ""


def extract_cms_authorization_credentials_name(all_user_class_dict) -> Dict:
    count = 0
    res = {}
    for cms, user_class_dict in all_user_class_dict.items():
        res[cms] = set([f"{i['name']}.{c['name']}" for i in user_class_dict for c in i['authorization_credentials']])
        count += len(res[cms])
    print(f"Authorization credentials: {count}")
    return res


def print_all_credentials(all_user_class_dict):
    tmp = []
    for _, user_class_dict in all_user_class_dict.items():
        tmp.extend(set([f"{i['name']}.{c['name']}" for i in user_class_dict for c in i['authorization_credentials']]))
    for i in tmp:
        print(i)
    

def extract_cms_all(all_user_class_dict):
    res = extract_cms_user_class_name(all_user_class_dict)
    res2 = extract_cms_authentication_credentials_name(all_user_class_dict)
    res3 = extract_cms_authorization_credentials_name(all_user_class_dict)
    data = [['cms', 'user class', 'authen cred', 'author cred']]
    for cms in all_user_class_dict.keys():
        data.append([cms, ", ".join(res[cms]), ", ".join(res2[cms]), ", ".join(res3[cms])])
    pd.DataFrame(data).to_csv(f"./Cache/cred.csv", index=False, header=False)


def search_class_info_by_cms_and_name(all_class_dict, cms, classname):
    for class_info in all_class_dict[cms]:
        if class_info['name'] == classname:
            return class_info
    return None


def filter_dict(all_class_info_dict) -> Dict:
    result = {}
    cms = DBS
    for k, v in all_class_info_dict.items():
        if k in cms:
            result[k] = v
    return result


def authentication_endswith(str, key):
    for k in key:
        if str.endswith(k):
            return True
    return False


def get_authentication_credentials(class_info) -> List:
    if not class_info['fields']:
        return []
    filter_fields = [f for f in class_info['fields'] if 'static' not in f['modifier'].lower()]
    authentication_cred = [f for f in filter_fields if authentication_endswith(f['name'].lower(), ['pass', 'token'])]
    if len(authentication_cred) > 1:
        authentication_cred = sorted(authentication_cred, key=len)
        for i in range(len(authentication_cred) - 1, 0, -1):
            if authentication_cred[0]['name'].lower() in authentication_cred[i]['name'].lower():
                del authentication_cred[i]
    if len(authentication_cred) != 0:
        return authentication_cred
    return []


def first_round_keyword_user_class(all_class_dict) -> Dict:
    res = {}
    for cms in all_class_dict:
        res[cms] = []
        cms_all_class_info_dict = all_class_dict[cms]
        for class_info in cms_all_class_info_dict:
            if class_info not in res[cms]:
                creds = get_authentication_credentials(class_info)
                if len(creds) != 0:
                    class_info['authentication_credentials'] = creds
                    res[cms].append(class_info)
    return res


def if_block_filter(cms) -> List[IFBlock]:
    if_block_obj_list = get_if_object_by_cms(cms)
    filter_if_block_list = []
    for if_block in if_block_obj_list:
        if not if_block.true_block.has_sso() and not if_block.true_block.has_interrupt():
            continue
        filter_if_block_list.append(if_block)
    return filter_if_block_list


def filter_by_inif_and_controllable(cms) -> List:
    if not USER_FIELDS:
        init_user_field()
        return USER_FIELDS[cms]
    else:
        return USER_FIELDS[cms]


def init_user_field():
    for cms in DBS:
        if_block_obj_list = if_block_filter(cms)
        used_fields = set()
        for if_block in if_block_obj_list:
            for cond in if_block.conditions:
                for f in cond.getter:
                    clazz, _, _field = f.split(".")
                    for var in cond.vars:
                        if var.type == clazz and not var.is_control:
                            used_fields.add(f"{clazz}.{_field}")
                            break
                for var in cond.vars:
                    if "." in var.name and var.name.islower() and not var.is_control:
                        clazz = var.type
                        field = var.name.split(".")[1]
                        used_fields.add(f"{clazz}.{field}")
        USER_FIELDS[cms] = list(used_fields)


def get_authorization_credentials_by_auth_if(all_user_class_dict):
    for cms, user_class_list in all_user_class_dict.items():
        increase = []

        user_class_names_dict = {}
        for user_class in user_class_list:
            if 'authorization_credentials' not in user_class.keys():
                user_class['authorization_credentials'] = []
            if 'authentication_credentials' not in user_class.keys():
                user_class['authentication_credentials'] = []
            user_class_names_dict[user_class['name']] = user_class
        
        if_block_obj_list = get_if_object_by_cms(cms)
        for block in if_block_obj_list:
            for cond in block.conditions:
                if block.is_auth_permission_check_by_interrupt() or cond.is_auth_condition_constant():
                    for i in cond.getter:
                        clazz, _, name = i.split(".")
                        if clazz in user_class_names_dict.keys():
                            for var in cond.vars:
                                if var.type == clazz:
                                    user_class = user_class_names_dict[clazz]
                                    for f in user_class['fields']:
                                        if f['name'] == name and f not in user_class['authentication_credentials']:
                                            if f not in user_class['authorization_credentials']:
                                                increase.append(f"{user_class['name']}.{f['name']}")
                                            user_class['authorization_credentials'].append(f)
                    for i in cond.vars:
                        if "." in i.name and i.name.islower():
                            clazz = i.type
                            field = i.name.split(".")[1]
                            if clazz in user_class_names_dict.keys():
                                user_class = user_class_names_dict[clazz]
                                for f in user_class['fields']:
                                    if f['name'] == field and f not in user_class['authentication_credentials']:
                                        if f not in user_class['authorization_credentials']:
                                            increase.append(f"{user_class['name']}.{f['name']}")
                                        user_class['authorization_credentials'].append(f)
    return all_user_class_dict


def match_field_semantics(field: str):
    for keyword in ['role', 'permission']:
        if keyword in field:
            return True
    return False


def get_authorization_credentials_by_semantics(all_user_class_dict):
    for cms, user_class_list in all_user_class_dict.items():
        for user_class in user_class_list:
            if 'authorization_credentials' not in user_class.keys():
                user_class['authorization_credentials'] = []
            potentials_fields = []
            for field in user_class['fields']:
                if match_field_semantics(field['name'].lower()) and "static" not in field["modifier"]:
                    potentials_fields.append(field)
            user_class['authorization_credentials'].extend(potentials_fields)
            if not user_class.get("authentication_credentials"):
                user_class['authentication_credentials'] = []
    return all_user_class_dict


def get_authorization_credentials_by_taint(all_user_class_dict):
    for cms, user_class_list in all_user_class_dict.items():
        taint_field = get_tainted_auth_fields(cms)
        for user_class in user_class_list:
            potentials_fields = []
            for field in user_class['fields']:
                if f"{user_class['name']}.{field['name']}" in taint_field:
                    potentials_fields.append(field)
                    print(f"{user_class['name']}.{field['name']}")
            user_class['authorization_credentials'].extend(potentials_fields)
            if not user_class.get("authentication_credentials"):
                user_class['authentication_credentials'] = []
    return all_user_class_dict


def get_filtered_credentials(all_user_class_dict) -> Dict:
    for cms, user_class_list in all_user_class_dict.items():
        used_fields = filter_by_inif_and_controllable(cms)
        other_fields = get_other_auth_fields(cms)
        for user_class in user_class_list:
            if 'authorization_credentials' not in user_class.keys():
                continue
            new_authorization_credential_list = []
            for authorization_credential in user_class['authorization_credentials']:
                authorization = f"{authorization_credential['class_name']}.{authorization_credential['name']}"
                if authorization in used_fields or authorization in other_fields:
                    new_authorization_credential_list.append(authorization_credential)
            user_class['authorization_credentials'] = new_authorization_credential_list
            new_authentication_credential_list = []
            for authentication_credential in user_class['authentication_credentials']:
                authentication = f"{authentication_credential['class_name']}.{authentication_credential['name']}"
                if authentication in used_fields or authentication in other_fields:
                    new_authentication_credential_list.append(authentication_credential)
            user_class['authentication_credentials'] = new_authentication_credential_list
    return all_user_class_dict


def filtered_credentials_by_type(all_user_class_dict: Dict):
    for _, user_class_list in all_user_class_dict.items():
        for user_class in user_class_list:
            credential_list = []
            for credential in user_class['authorization_credentials']:
                if credential["type"].lower() in BASE_CLASS:
                    credential_list.append(credential)
            user_class['authorization_credentials'] = credential_list
            authen_credential_list = []
            for credential in user_class['authentication_credentials']:
                if credential["type"].lower() in BASE_CLASS:
                    authen_credential_list.append(credential)
            user_class['authentication_credentials'] = authen_credential_list
    return all_user_class_dict


def evaluate(all_user_class_dict):
    import pandas as pd
    import re
    GT = 0
    AUTHEN_TP = 0
    TP = 0
    FP = 0
    FN = 0
    df_gt = pd.read_excel("./Input/credentials.xlsx", sheet_name='candidate')
    for _, row in df_gt.iterrows():
        cms = row['CMS']
        authen_cred_gt = set([c.strip() for c in re.split(r"[,\s]+", row['Authentication Credentials GT'])])
        author_cred_gt = set([c.strip() for c in re.split(r"[,\s]+", row['Authorization Credentials GT'])])
        authen_cred = set([f"{i['name']}.{c['name']}" for i in all_user_class_dict[cms] for c in i['authentication_credentials']])
        author_cred = set([f"{i['name']}.{c['name']}" for i in all_user_class_dict[cms] for c in i['authorization_credentials']])
        print("--------------------")
        print(cms)
        print(f"authentication_credentials TP: {authen_cred_gt & authen_cred}")
        print(f"authentication_credentials FP: {authen_cred-authen_cred_gt}")
        print(f"authentication_credentials FN: {authen_cred_gt-authen_cred}")
        AUTHEN_TP += len(authen_cred_gt & authen_cred)
        TP += len(authen_cred_gt & authen_cred)
        FP += len(authen_cred-authen_cred_gt)
        FN += len(authen_cred_gt-authen_cred)
        print(f"authorization_credentials TP: {author_cred_gt & author_cred}")
        print(f"authorization_credentials FP: {author_cred-author_cred_gt}")
        print(f"authorization_credentials FN: {author_cred_gt-author_cred}")
        TP += len(author_cred_gt & author_cred)
        FP += len(author_cred-author_cred_gt)
        FN += len(author_cred_gt-author_cred)
    print(f"{TP} {FP} {FN} {AUTHEN_TP}")
    print(f"precision: {TP/(TP+FP)}")
    print(f"recall: {TP/(TP+FN)}")


def get_credentials():
    all_class_info_dict = filter_dict(load_json("./Input/all_class_dict.json"))

    all_user_class_dict = first_round_keyword_user_class(all_class_info_dict)
    extract_cms_authentication_credentials_name(all_user_class_dict)

    all_user_class_dict = get_authorization_credentials_by_auth_if(all_class_info_dict)
    extract_cms_authentication_credentials_name(all_user_class_dict)
    extract_cms_authorization_credentials_name(all_user_class_dict)

    all_user_class_dict = get_authorization_credentials_by_semantics(all_class_info_dict)
    all_user_class_dict = filtered_credentials_by_type(all_user_class_dict)
    extract_cms_authentication_credentials_name(all_user_class_dict)
    extract_cms_authorization_credentials_name(all_user_class_dict)

    all_user_class_dict = get_authorization_credentials_by_taint(all_user_class_dict)
    extract_cms_authentication_credentials_name(all_user_class_dict)
    extract_cms_authorization_credentials_name(all_user_class_dict)

    loop_flag = True
    x = 0
    while loop_flag:
        x += 1
        all_user_class_dict, loop_flag = find_user_credentials_by_frequency(all_user_class_dict)
    all_user_class_dict = filtered_credentials_by_type(all_user_class_dict)
    extract_cms_authentication_credentials_name(all_user_class_dict)
    extract_cms_authorization_credentials_name(all_user_class_dict)

    return all_user_class_dict


if __name__ == "__main__":
    all_user_class_dicts = get_credentials()
    evaluate(all_user_class_dicts)