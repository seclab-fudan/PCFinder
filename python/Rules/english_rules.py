#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import re

def method_pattern_generator():
    patterns = []
    verbs = []
    nouns = []
    owners = []
    operations = []

    operations_pattern = "^(?!"
    for op in operations:
        operations_pattern += op + "|"
    operations_pattern = operations_pattern[:-1]
    operations_pattern += ")"

    verb_pattern1 = "("
    for verb in verbs:
        verb_pattern1 += verb + "|"
    verb_pattern1 = verb_pattern1[:-1]
    verb_pattern1 += ")"

    noun_pattern1 = "("
    for noun in nouns:
        noun_pattern1 += noun + "|"
    noun_pattern1 = noun_pattern1[:-1]
    noun_pattern1 += ")"

    verb_pattern2 = "("
    for verb in verbs:
        if verb in ["get"]:
            continue
        verb_pattern2 += verb + "|"
    verb_pattern2 = verb_pattern2[:-1]
    verb_pattern2 += ")"

    owner_pattern2 = "("
    for owner in owners:
        owner_pattern2 += owner + "|"
    owner_pattern2 = owner_pattern2[:-1]
    owner_pattern2 += ")"

    pattern_1 = f"{operations_pattern}.*{verb_pattern1}.*{noun_pattern1}"
    pattern_2 = f"{operations_pattern}.*{verb_pattern2}.*{owner_pattern2}$"

    patterns.append(pattern_1)
    patterns.append(pattern_2)

    return patterns


def auth_english_rule_analysis(strs: str):
    for pattern in METHOD_PATTERNS:
        res = re.findall(pattern, strs.lower(), re.IGNORECASE)
        if res:
            return True
    return False


METHOD_PATTERNS = method_pattern_generator()
