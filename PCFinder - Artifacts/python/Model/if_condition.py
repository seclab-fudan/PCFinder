#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# here put the import lib

from typing import List, TypeVar

from Basic.utils import init_user_related_class
from Model.if_method import IFMethod
from Model.if_var import IFVar
from Rules.english_rules import auth_english_rule_analysis
import json

T = TypeVar('T', bound='IFCondition')


class IFCondition:
    def __init__(self, cms, condition_loc, condition_content=None, condition_vars=None, condition_methods=None):
        """

        :param cms:
        :param condition_loc: if condition loc
        :param condition_content: the content of the condition
        :param condition_vars: the list of IFVar objects
        :param condition_methods: the list of IFMethod objects
        """
        self.cms = cms
        self.loc = condition_loc
        self.content: str = condition_content
        self.vars: List[IFVar] = condition_vars
        self.methods: List[IFMethod] = condition_methods
        self.getter: List[str] = []
        self.auth_confidence = 0  # the confidence of the condition is related to Auth
        self.if_block = None

    def is_contain_user_related_vars(self):
        all_user_class_info = json.load(open(f'./Cache/all_user_related_class_dict_taint.json', 'r'))
        now_cms = all_user_class_info[self.cms]
        user_class_name_list = []
        for class_info in now_cms:
            user_class_name_list.append(class_info['name'])

        if self.methods:
            for method in self.methods:
                if method.return_type in user_class_name_list:
                    return True
        if self.vars:
            for var in self.vars:
                if var.is_user_related:
                    return True
        return False

    def is_contain_uncontrol_user_related_vars(self):
        all_user_class_info = json.load(open(f'Cache/all_user_related_class_dict_taint.json', 'r'))
        now_cms = all_user_class_info[self.cms]
        user_class_name_list = []
        for class_info in now_cms:
            user_class_name_list.append(class_info['name'])

        for method in self.methods:
            if method.return_type in user_class_name_list:
                return True
        for var in self.vars:
            if var.is_user_related and not var.is_control:
                return True
        return False

    def is_contain_control_vars(self):
        if self.vars:
            for var in self.vars:
                if var.is_control:
                    return True
        return False

    def is_all_control_vars(self):
        if self.vars and len(self.vars) >= 2:
            for var in self.vars:
                if var.is_control is None:
                    return False
        else:
            return False
        return True

    def is_auth_condition_constant(self):
        for method in self.methods:
            if auth_english_rule_analysis(method.name_body.replace("this.", "")):
                return True
        return False

    def has_user_related_method_with_boolean_return(self):
        user_related_class = init_user_related_class()
        for method in self.methods:
            if method.return_type == "boolean" and method.package in user_related_class:
                return True

    def normalize(self, cond: T):
        var_names = set([i.name if '"' in i.name or "'" in i.name else i.type for i in cond.vars])
        method_names = set([i.method_name_body() for i in cond.methods])
        return ",".join(list(var_names) + list(method_names))

    def __eq__(self, other: T):
        if self.normalize(self) == self.normalize(other):
            return True
        else:
            return False

    def __hash__(self):
        return hash(self.normalize(self))
