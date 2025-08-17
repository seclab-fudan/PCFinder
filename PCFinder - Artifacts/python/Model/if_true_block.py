#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# here put the import lib
from typing import Dict, List
from Rules.english_rules import *


class IFTrueBlock:
    def __init__(self, cms, if_loc):
        """
        if true block

        :param cms:
        :param if_loc:
        :param type: SSO, Return, Throw, Redirect
        :param interrupt_content:
        :param interrupt_info: dict, key is self.type
        :param sso_content
        """
        self.cms = cms
        self.loc = if_loc
        self.type = []
        self.interrupt_content: List[str] = []
        self.interrupt_info: Dict = {}
        self.auth_confidence = 0  # the confidence of the if-true is related to Auth
        self.sso_content: List[str] = []

    def is_auth_interrupt_str(self):
        if self.interrupt_info != {}:
            for _type, info in self.interrupt_info.items():
                string_content = info['if_str']
                if string_content == "":
                    continue
                if _type in ['redirect']:
                    return True
                if _type in ['throw', 'return']:
                    if auth_english_rule_analysis(string_content):
                        return True
        return False

    def is_auth_interrupt_constant(self):
        if self.interrupt_info != {}:
            for _type, info in self.interrupt_info.items():
                constant_string = info['if_const']
                if constant_string == '':
                    continue
                constant_strings = constant_string.split('<DOT>')
                for constant_string in constant_strings:
                    if '"' in constant_string or "'" in constant_string:
                        continue
                    if _type in ['throw', 'return'] and (
                            auth_english_rule_analysis(constant_string)
                    ):
                        return True
                    if _type in ['redirect']:
                        return True
        return False

    def is_auth_interrupt_block(self):
        if self.is_auth_interrupt_str() or self.is_auth_interrupt_constant():
            return True
        return False

    def has_sso(self):
        return 'SSO' in self.type

    def has_interrupt(self):
        return any(i in self.type for i in ['Throw', 'Return', 'Redirect'])

    def normalize(self, cond):
        result = set()
        for _type, info in self.interrupt_info.items():
            string_content = info['if_str']
        return string_content

    def __eq__(self, other):
        if self.normalize(self) == self.normalize(other):
            return True
        else:
            return False

