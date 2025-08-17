#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# here put the import lib
from Rules.english_rules import *
import re


class IFMethod:
    def __init__(self, cms, method_loc, method_name, method_return_type):
        """

        :param cms:
        :param method_loc:
        :param method_name:
        :param method_return_type: the return type of the method
        """
        self.cms = cms
        self.loc = method_loc
        self.name = method_name
        self.return_type = method_return_type
        self.package = self.method_package()
        self.name_body = self.method_name_body()
        self.is_user_related = None
        self.auth_confidence = 0  # the confidence of the method is related to Auth

    def show(self):
        print(f"method: {self.name}\n"
              f"return_type: {self.return_type}\n")

    def method_name_body(self):
        """
        :return: a.b() -> return b
        """
        method_split = self.name.split('.')
        if len(method_split) == 1:
            return self.name
        else:
            return method_split[1]

    def method_package(self):
        """
        :return: a.b() -> return a
        """
        method_split = self.name.split('.')
        if len(method_split) == 1:
            return ''
        else:
            return method_split[0]

    def is_auth_name(self) -> bool:
        """

        :return: True is auth-keywords related; False is others
        """
        for pattern in METHOD_PATTERNS:
            res = re.findall(pattern, self.name_body, re.IGNORECASE)
            if res:
                return True
        return False

    def is_auth_package(self) -> bool:
        for pattern in METHOD_PATTERNS:
            res = re.findall(pattern, self.package, re.IGNORECASE)
            if res:
                return True
        return False

    def calc_auth_confidence(self):
        return self.auth_confidence
