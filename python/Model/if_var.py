#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# here put the import lib


class IFVar:
    def __init__(self, cms, var_loc, var_name, var_type):
        """

        :param cms:
        :param var_loc:
        :param var_name:
        :param var_type: variable type
        :param var_source: the source of the variable (source_name)
        :param source_type: source type of variable (e.g., http, session, database)
        :param is_control: True or False, True is controllable
        """
        self.cms = cms
        self.loc = var_loc
        self.name = var_name
        self.type = var_type
        self.source = None
        self.source_type = None
        self.is_control = 0
        self.is_user_related = None
        self.auth_confidence = 0  # the confidence of the variable is related to Auth

    def show(self):
        print(f"var: {self.name}\n"
              f"type: {self.type}\n"
              f"source: {self.source}\n"
              f"source_type: {self.source_type}\n"
              f"is_control: {self.is_control}\n")

    def calc_auth_confidence(self):
        return self.auth_confidence

