#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# here put the import lib
from typing import List, Type, TypeVar

from Model.if_condition import IFCondition
from Model.if_true_block import IFTrueBlock

T = TypeVar('T', bound='IFBlock')

class IFBlock:
    def __init__(self, cms, if_loc, if_true_block=None):
        """
        root class, stored all info of if block

        :param cms:
        :param if_loc: if condition loc
        :param conditions: list of IFCondition objects
        :param if_true_block: IFTrueBlock object
        :param if_content:
        :param wrapper_method: the wrapper method of if block
        :param wrapper_return_type: the return type of wrapper method
        """
        self.cms = cms
        self.loc = if_loc
        self.conditions: List[IFCondition] = []
        self.conditions_content: str = ""
        self.true_block: IFTrueBlock = if_true_block
        self.content: str = ""
        self.wrapper_method = ""
        self.wrapper_return_type = ""
        self.is_aop = False
        self.if_position = ""
        self.method_name = ""
        self.public_if = False
        self.gt = 0  # ground truth
        self.tool_res = 0  # results of tool
        self.isauth = 0  # 1 is permission check, 0 is not

    def has_user_related_vars_in_condition(self):
        for condition in self.conditions:
            if condition.is_contain_user_related_vars():
                return True
        return False

    def is_auth_permission_check_by_user(self):
        for condition in self.conditions:
            if condition.is_contain_uncontrol_user_related_vars():
                self.isauth = 1
                return True
        return False

    def is_auth_permission_check_by_interrupt(self):
        if self.true_block.is_auth_interrupt_block():
            return True
        return False

    def is_auth_permission_check_by_condition(self):
        for cond in self.conditions:
            if cond.is_auth_condition_constant():
                return True
        return False

    def normalize(self):
        hash_dict = []
        for i in self.conditions:
            hash_dict.append(str(hash(i)))
        return "|".join(hash_dict)

    def __hash__(self):
        return hash(self.normalize())

    def __eq__(self, other: T):
        if set(self.conditions) == set(other.conditions):
            return True
        else:
            return False
