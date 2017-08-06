#! /usr/bin/env python3.5

import json
from os import path, getcwd

settings_path = path.join(getcwd(), "config", "settings.json")

# config file constants ########################################################

with open(settings_path) as settings_file:
    config = json.load(settings_file)
try:
    # grade info
    GRADE_JSON_PATH = config["grades"]["path"]

    # course info
    COURSE_NAME = config["course"]["name"]
    COURSE_DIR = config["course"]["path"]
    GRADER_EMAIL = config["grader_email"]

    # smtp server
    SMT_SERV = config["smt"]["server"]
    SMT_PORT = config["smt"]["port"]

    # credentials
    SMT_USER = config["smt"]["user"]
    SMT_PASS = config["smt"]["pass"]
except KeyError:
    sys.stderr.write('Setting value missing at %s\n' % settings_file)
    sys.exit(1)

# support file path prefixes ###################################################

SUPPORT_DIR_NAME = "support_files"
ALT_MAIN_PATH_PREFIX = path.join(getcwd(), SUPPORT_DIR_NAME, "alt_main")
GRADING_CRITERIA_PATH_PREFIX = path.join(getcwd(), SUPPORT_DIR_NAME, "grading_criteria")
REQUIRED_FILES_PATH_PREFIX = path.join(getcwd(), SUPPORT_DIR_NAME, "required_files")
TEST_FILES_PATH_PREFIX = path.join(getcwd(), SUPPORT_DIR_NAME, "test_files")

# result file path prefixes ####################################################

RESULTS_PATH_PREFIX = path.join(getcwd(), "results")

# default error strings ########################################################

TIMEOUT_MSG = ("Execution timed out. The most common reason for this is an "
             + "infinite loop.\n")

MISSING_MSG = ("Homework file/directory not found.\n" +
               "  If you completed this homework, contact instructor.\n" +
               "  DO NOT modify your hw directory in any way, as this will " +
               "mark it as late.\n\n")

# miscellaneous ################################################################

DIVIDER = "\n--------------------------------------------------------------------------------\n\n"
