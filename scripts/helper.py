#!/usr/bin/env python3

# General purpose python functions

import os
import subprocess
import pmsg
import re
import re


class helper():
    """
    Class used to provide general purpose python functions.
    """


# ########################################################
def __init__(self):
    pass


# ########################################################
def run_a_command(command):
    """
    :param command: String of command and all its arguments.
    :returns: Integer - Returns the number of errors the command caused.
    :rtype: int
    """

    # Split up 'command' so it can be run with the subprocess.run method...
    pmsg.running(command)
    cmd_parts = command.split()
    myenv = dict(os.environ)
    returns = subprocess.run(cmd_parts, env=myenv)
    return returns.returncode

#############################################################
def check_for_result(command_and_args_list, expression):
    """Checks to see if a given command returns an expected value.

    Args:
        command_and_args_list (list): Run this command with arguments and capture the output.
        expression (string): Split the result of the command into lines and see if any line matches this expression.
    :returns: Boolean - Match or no match
    :rtype: Boolean
    """

    # Run the command capturing the stdout
    process = subprocess.Popen(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = process.communicate()
    lines = output.splitlines()
    for line in lines:
        if re.search(expression, line.decode("utf-8")) is not None:
            return True
    return False


def check_for_result_for_a_time(command_and_args_list, expression, check_how_often, max_checks):
    """
    Run a command with arguments and check the output for a specific string of text (regular expression) over a time period.
    
    Args:
        command_and_args_list (list): Run this command with arguments and capture the output.
        expression (string): Split the result of the command into lines and see if any line matches this expression.
        check_how_often (int): check every <check_how_often> seconds for the expression.
        max_checks (int): check a maxiumum of this many times before giving up.
        
    :returns: Boolean - Match or no match
    :rtype: Boolean

    """
    found = False
    for i in range(30):
        if check_for_result(["tanzu", "package", "repository", "list", "-A"], expression):
            found = True
            break
        time.sleep(check_how_often)

    if not found:
        return False
    return True