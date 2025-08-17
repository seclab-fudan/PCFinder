#!/usr/bin/env python
# -*- coding: utf-8 -*-

# here put the import lib
import re
from collections import Counter
import itertools
from typing import List, Dict, Tuple
import pandas as pd
from mlxtend.frequent_patterns import apriori
from mlxtend.preprocessing import TransactionEncoder


def get_field_by_name(fields, field_name):
    for f in fields:
        if f["name"] == field_name:
            return f


def extract_cms_user_class_name(all_user_class_dict) -> List:
    res = []
    for _, user_class_dict in all_user_class_dict.items():
        res += [i['name'] for i in user_class_dict]
    return res


def extract_cms_user_field_name(all_user_class_dict) -> List:
    res = set()
    for _, user_class_dict in all_user_class_dict.items():
        for user_class in user_class_dict:
            for authorization_credentials in user_class['authorization_credentials']:
                res.add(authorization_credentials["name"])
    return list(res)


def find_frequent_itemsets(data, min_support, keyword):
    # transfer to one-hot
    te = TransactionEncoder()
    te_ary = te.fit(data).transform(data)
    # one-hot -> DataFrame
    df = pd.DataFrame(te_ary, columns=te.columns_)
    # ues apriori
    frequent_itemsets = apriori(df, min_support=min_support, use_colnames=True)
    user_frequent_itemsets = frequent_itemsets[frequent_itemsets['itemsets'].apply(lambda x: keyword in x)]
    patterns = []
    for itemset in user_frequent_itemsets['itemsets']:
        if len(list(itemset)) == 1:
            continue
        else:
            patterns.append(list(itemset))
    return patterns


def get_final_frequency_keyword_lst(initial_words, words_list, list_length=3, threshold=0.05, _type="class"):
    count = Counter(initial_words)
    sorted_count = sorted(count.items(), key=lambda x: x[1], reverse=True)
    frequency_keywords = []
    frequency_list = []
    for word, frequency in sorted_count:
        if frequency not in frequency_list and len(frequency_list) == list_length:
            break
        if frequency not in frequency_list:
            frequency_list.append(frequency)
        frequency_keywords.append(word)
    final_frequency_keyword_lst = []
    if _type == "class":
        split_lst = [re.findall(r'[A-Z]?[a-z]+', name) for name in words_list]
    else:
        split_lst = [[i.lower() for i in re.findall(r'[A-Z]?[a-z]+', name)] for name in words_list]
    for frequency_keyword in frequency_keywords:
        frequent_patterns = find_frequent_itemsets(data=split_lst, min_support=threshold, keyword=frequency_keyword)
        frequency_keyword = [frequent_pattern for frequent_pattern in frequent_patterns
                             if frequent_pattern not in final_frequency_keyword_lst]
        final_frequency_keyword_lst.extend(frequency_keyword)
    return final_frequency_keyword_lst


def classname_frequency_analysis(words_list, threshold=0.05, _type="class"):
    if _type == "class":
        initial_words = [word for name in words_list for word in re.findall(r'[A-Z]?[a-z]+', name)]
        final_frequency_keyword_lst = get_final_frequency_keyword_lst(initial_words, words_list, threshold=threshold,
                                                                      list_length=2, _type=_type)
    else:
        initial_words = [word.lower() for name in words_list for word in re.findall(r'[A-Z]?[a-z]+', name)]
        # TODO normalize
        initial_words = [word.replace("permissions", "permission") for word in initial_words]
        initial_words = [word.replace("roles", "role") for word in initial_words]
        initial_words = [word.replace("ids", "id") for word in initial_words]
        final_frequency_keyword_lst = get_final_frequency_keyword_lst(initial_words, words_list, threshold=threshold,
                                                                      list_length=6, _type=_type)
    return final_frequency_keyword_lst


def find_user_class_by_frequency(all_class_dict, all_user_class_dict):
    res = all_user_class_dict
    words_list = extract_cms_user_class_name(all_user_class_dict)
    final_frequency_keyword_lst = classname_frequency_analysis(words_list, threshold=0.05)
    for cms in all_class_dict:
        increase = []
        cms_all_class_info_dict = all_class_dict[cms]
        for class_info in cms_all_class_info_dict:
            name = class_info['name']
            objs = class_info['objs']
            for keyword_pattern in final_frequency_keyword_lst:
                flag = True
                for keyword in keyword_pattern:
                    if keyword not in name:
                        flag = False
                if flag and objs != []:
                    if class_info not in res[cms]:
                        class_info['authentication_credentials'] = []
                        class_info['authorization_credentials'] = []
                        res[cms].append(class_info)
                        increase.append(class_info['name'])
                        break
    return res


def gen_fields(field_keyword: List):
    tmp_field_keyword = []
    result_field = set()
    for f in field_keyword:
        tmp_field_keyword.append(f"{f[0].upper()}{f[1:]}")
    permutations_field = [''.join(permutation) for permutation in itertools.permutations(tmp_field_keyword)]
    for field in permutations_field:
        result_field.add(f"{field[0].lower()}{field[1:]}")
    return result_field


def check_field_exist(auth_cred: List, new_field: str):
    for i in auth_cred:
        if i["name"] == new_field:
            return True
    return False


def find_user_credentials_by_frequency(all_user_class_dict) -> Tuple[Dict, bool]:
    result_fields_set = set()
    new_fields = set()
    flag = False
    words_list = extract_cms_user_field_name(all_user_class_dict)
    final_frequency_keyword_lst = classname_frequency_analysis(words_list, threshold=0.001, _type="field")
    print(final_frequency_keyword_lst)
    for field_keyword in final_frequency_keyword_lst:
        for f in gen_fields(field_keyword):
            new_fields.add(f)

    for cms, cms_all_user_class_dict in all_user_class_dict.items():
        for class_info in cms_all_user_class_dict:
            fields_name = [field['name'] for field in class_info['fields']]
            objs = class_info['objs']

            for new_field in new_fields:
                if new_field in fields_name and objs != [] and not check_field_exist(
                        class_info["authorization_credentials"],
                        new_field):
                    result_fields_set.add(new_field)
                    flag = True
                    field = get_field_by_name(class_info['fields'], new_field)
                    class_info["authorization_credentials"].append(field)
    print(result_fields_set)
    return all_user_class_dict, flag
