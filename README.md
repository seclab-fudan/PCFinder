# PCFinder Artifact

Welcome!
This document will guide you through the installation and running of PCFinder.

## Setup
PCFinder consists of two parts: CodeQL code and Python code. We will explain how to set up each of them respectively.

### CodeQL

First, you can quickly install CodeQL following the link below: [CodeQL Setup](https://docs.github.com/en/code-security/codeql-cli/getting-started-with-the-codeql-cli)

Then, you can build a CodeQL database for the target application using the following command:
```
codeql database create <database> --language=<language-identifier>
```

### Python
After generating the database, execute the following commands in order to identify the permission checks in the application.
```
python3 Basic/run_if_ql.py
python3 Basic/codeql_parser.py
python3 pcfinder.py
```

## Dataset
The dataset for the evaluation part of PCFinder is located in the `dataset` folder, where each line corresponds to a CMS name and GitHub url.

## Empirical Data
The `Empirical Study-Permission Check Label.json` and `Evaluation-Permission Check GT.json` files in the `empirical data` directory record the labeling of permission checks during our empirical study and the construction of the ground truth for evaluation, respectively.