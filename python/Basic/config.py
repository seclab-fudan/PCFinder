#!/usr/bin/env python
# -*- coding: utf-8 -*-


# here put the import lib

LD_PATH = ".m2/repository"

config = "2"

SRC_PATH = "./srcs/src_if_all_newest/"
DB_PATH = "./dbs/dbs_if_all/"
OUTPUT_PATH = "./Basic/result/"

DBS = """PublicCMS
FlyCms
litemall
opsli-boot
mogu_blog_v2
mall
DimpleBlog
xmall
SENS
novel-plus
itranswarp
newbee-mall-plus
lamp-cloud
shop-mall
mall4j
newbee-mall
MMall
dts-shop
my-shop
ForestBlog
novel
My-Blog
Spring-Cloud-Platform
unimall
RuoYi
SpringBootBlog
newblog
zrlog
My-Blog-layui
youlai-mall""".split('\n')

QL_PATH = "./vscode-codeql-starter/codeql-custom-queries-java/"

IF_CONTENT_SARIF_PATH = f"{OUTPUT_PATH}/if_content_result/"

IF_TRUE_THROW_SARIF_PATH = f"{OUTPUT_PATH}/if_throw_result/"
IF_TRUE_RETURN_SARIF_PATH = f"{OUTPUT_PATH}/if_return_result/"
IF_TRUE_REDIRECT_SARIF_PATH = f"{OUTPUT_PATH}/if_redirect_result/"
IF_TRUE_SSO_SARIF_PATH = f"{OUTPUT_PATH}/if_true_sso_result/"
IF_AOP_SARIF_PATH = f"{OUTPUT_PATH}/if_aop/"
IF_PUBLIC_SARIF_PATH = f"{OUTPUT_PATH}/if_public/"

# if condition
IF_COND_VAR_METHOD_SARIF_PATH = f"{OUTPUT_PATH}/if_cond_var_method_result/"
IF_COND_VAR_SARIF_PATH = f"{OUTPUT_PATH}/if_cond_var_result/"
IF_COND_CONTROL_VAR_SARIF_PATH = f"{OUTPUT_PATH}/if_cond_control_result/"

ALL_CLASS_SARIF_PATH = f"{OUTPUT_PATH}/all_class_result/"
ALL_CLASS_EXTENDED_SARIF_PATH = f"{OUTPUT_PATH}/all_class_extended_result/"
USER_RELATED_EXTENDED_SARIF_PATH = f"{OUTPUT_PATH}/user_related_extended_result/"
CREDENTIALS_SARIF_PATH = f"{OUTPUT_PATH}/credentials_result/"

UTILITY_PDG_PATH = f"{OUTPUT_PATH}/utility_pdg_result/"
UTILITY_CFG_PATH = f"{OUTPUT_PATH}/utility_cfg_result/"

### result
IF_RESULT_PATH = f"{OUTPUT_PATH}/if_all_result/"

### ql suffix
IF_CONTENT_SUFFIX = "content"
IF_TRUE_THROW_SUFFIX = "throw"
IF_TRUE_RETURN_SUFFIX = "return"
IF_TRUE_SSO_SUFFIX = "true_sso"
IF_COND_VAR_METHOD_SUFFIX = "var_method"
IF_COND_CONTROL_VAR_SUFFIX = "control"
TRUSTED_IF_SUFFIX = "trusted"
ALL_CLASS_SUFFIX = "class"
ALL_CLASS_EXTENDED_SUFFIX = "class_extended"
USER_RELATED_EXTENDED_SUFFIX = "user_related_extended"
IF_TRUE_REDIRECT_SUFFIX = "redirect"
CREDENTIALS_SUFFIX = "credentials"

SEP = "<SEP>"
CRLF = "<CRLF>"
SPLIT = "<SPLIT>"
DOT = "<DOT>"

### CodeQL Config
RUN_QL_THREAD_NUM = 10
CODEQL_THREAD_NUM = 1024
# MAX_PATH = 2
CODEQL_RAM = 102400
