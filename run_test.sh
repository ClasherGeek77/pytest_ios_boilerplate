#!/bin/bash
cd "$(dirname "$0")"

# what runs, edit here or give an argument, variants:
#   TEST_PATH="tests/"                                                          everything
#   TEST_PATH="tests/test_login_errors.py"                                      one file
#   TEST_PATH="tests/test_login_errors.py::test_locked_out_user_is_refused"     one test
#   TEST_PATH="tests/ -k locked"                                                tests whose name contains "locked"
#   TEST_PATH="tests/ -x"                                                       stop at the first failure
TEST_PATH="tests/"

# report file name, written to reports/, edit this line to change it, variants:
#   REPORT_NAME=""                  default: report_<run timestamp>_<test path>.html
#   REPORT_NAME="smoke.html"        a fixed name (overwritten by the next run)
REPORT_NAME=""

export TEST_PATH REPORT_NAME

exec ./run_engine.sh "$@"
