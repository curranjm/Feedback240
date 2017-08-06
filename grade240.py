#! /usr/bin/env python3.5

import argparse
from datetime import datetime, timezone, timedelta
import difflib
import json
import os
from config.settings240 import *
from shutil import rmtree
import subprocess
import sys
import time


# CONSTANTS ####################################################################

EST = timezone(timedelta(-1, 68400))
DEADLINE_DT = datetime(2017, 7, 31, 0, 00, tzinfo=EST)
DEADLINE = time.mktime(DEADLINE_DT.timetuple())


# METHODS ######################################################################

################################################################################
# config methods
################################################################################

def config_argparser():
    """
    Sets up command line options using argparse and returns the argparse
    argument parser object.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("homework",
                        help="The homework to grade (e.g., hw1)")
    parser.add_argument("-c99",
                        "--c99mode",
                        help="Compile in c99 mode",
                        action="store_true")
    parser.add_argument("-u",
                        "--unixname",
                        help="Grade the specified unix name only")
    parser.add_argument("-n",
                        "--notes",
                        help="Include if this homework asks for notes.txt",
                        action="store_true")
    parser.add_argument("-a",
                        "--altmain",
                        help="Provide a custom main file",
                        action="store_true")
    parser.add_argument("-d",
                        "--diff",
                        help="Include to show diff output in report file",
                        action="store_true")
    parser.add_argument("-m",
                        "--make",
                        help="Include if this homework should be compiled with a makefile",
                        action="store_true")
    return parser

################################################################################
# submission time methods
################################################################################

def time_submitted(file_path):
    """
    Gets the time a file was last modified.
    Args:
        file_path (str): the path to the file whose last edit time is desired.
    Returns:
        float: epoch time of last modification time of filepath as a float.
    """
    last_mod_ts = time.localtime(os.path.getmtime(file_path))
    return time.mktime(last_mod_ts)

def format_time(time_float):
    """
    Formats an epoch time float as a day/time string.
    Args:
        time_float (float): Epoch time to format.
    Returns:
        str: the input time in the format month-day-year hour:minute
    """
    tt = time.localtime(time_float)
    return time.strftime('%m-%d-%Y %H:%M', tt)

def is_late(time_submitted):
    """
    Determine if a submittal time is past the deadline.
    Args:
        time_submitted (float): an epoch time as a float.
    Returns:
        bool: True if homework was submitted late.
              False if homework was submitted on time.
    """
    if time_submitted - DEADLINE > 500:
        return True
    else:
        return False

def check_submission_time(list_of_files, output, hw):
    """
    For each file in a list, determine whether it was submitted late or not and
    write the result to the provided output file.
    Args:
        list_of_files (obj): A list of file paths to check.
        output (obj): The file object to write results to.
        hw (str): The homework being graded (e.g., "hw2").
    """
    for fp in list_of_files:
        output.write(format_time(DEADLINE) + " (" + hw + " deadline)\n")
        output.write(format_time(time_submitted(fp)) +
                    " (" + os.path.basename(os.path.normpath(fp)) +
                    " submission time)\n")
        if is_late(time_submitted(fp)):
            output.write("LATE SUBMISSION.\n")
    output.write(DIVIDER)

################################################################################
# compile and run methods
################################################################################

def run(command, stdin = None, timeout = 5):
    """
    Invokes an executable in the shell and returns the output as a string.
    Args:
        command (str): The string to execute in the shell.
        stdin(:string): File to be treated as standard in.
        timeout(:int): How long to wait (in seconds) before timing out.
    Returns:
        str: The output produced by the command being executed or "__TIMEOUT__"
             if the command fails to complete within specified timeout.
    """
    try:
        if not stdin is None:
            in_file = open(stdin, 'r')
            cp = subprocess.run(command.split(),
                                stdin=in_file,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                timeout=timeout,
                                universal_newlines=True)
            in_file.close()
            return cp.stdout
        else:
            cp = subprocess.run(command.split(),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                timeout=timeout,
                                universal_newlines=True)
            return cp.stdout
    except subprocess.TimeoutExpired:
        return "__TIMEOUT__"

def compile(source_path_list, exec_path, gccflags=''):
    """
    Compile C source code.
    Args:
        source_path_list(obj): A list of paths to required source files.
        exec_path(str): The path to the executable.
        gccflags(str): A string containing any gcc flags to compile with.
    Returns:
        bool: True if compilation was successful, False otherwise.
        str: A string describing the compilation result, including errors.
    """
    sources = " ".join(source_path_list)
    output = run("gcc " + gccflags + " %s -o %s" % (sources, exec_path))
    if "error" in output:
        return (False,
                "COMPILATION FAILURE (" +
                os.path.basename(os.path.normpath(exec_path)) +
                ")\n" + output + "\n")
    else:
        return(True, "COMPILATION SUCCESSFUL (" +
               os.path.basename(os.path.normpath(exec_path)) +
               ")\n")

################################################################################
# misc helpers
################################################################################

def active_students(path_to_json):
    """
    Generates a list containing the unix account names of all active students.
    Args:
        path_to_json (str): Path to the json file for the class.
    Returns:
        obj: A list of unix name strings.
    """
    with open(path_to_json) as data_file:
        data = json.load(data_file)
    students = []
    for student in data:
        if student["withdrawn"] == 0:
            students.append(student["unixName"])
    return students

def empty_dir(dir_path):
    """
    Deletes files from provided path.
    Args:
        dir_path (str): The path to the directory to empty.
    """
    if os.path.isdir(dir_path):
        rmtree(dir_path)
    os.mkdir(dir_path)

def get_gc_string(hw):
    """
    Gets the grading criteria for the homework currently being graded
    as a string. Ends process if grading criteria is not found.
    Args:
        hw (str): The homework currently being graded (e.g., "hw2").
    Returns:
        str: The grading criteria or "Error: grading criteria not found."
    """
    try:
        gc_path = os.path.join(GRADING_CRITERIA_PATH_PREFIX, hw + "_gc.txt")
        with open(gc_path,'r') as f:
            return f.read() + "\n"
    except IOError:
        print("Error: Unable to find grading criteria for " + hw + ".")
        sys.exit()

def get_rf_list(hw):
    """
    Gets the required files for this homework as a list.
    Ends process if required file list is not found.
    Args:
        hw (str): The homework currently being graded (e.g., "hw2").
    Returns:
        obj: A list of required file name strings.
    """
    try:
        rf_path = os.path.join(REQUIRED_FILES_PATH_PREFIX, hw + "_rf.txt")
        files = []
        with open(rf_path,'r') as f:
            for line in f:
                files.append(line[:-1])
        return files
    except IOError:
        print("Error: Unable to find required files for " + hw + ".")
        sys.exit()


def print_source(list_of_files, output):
    """
    Send a list of source files to output, separated by dividers.
    """
    for src in list_of_files:
        with open(src,'r') as f:
            output.write("SOURCE CODE (" +
                         os.path.basename(os.path.normpath(src)) + "):\n")
            output.write(f.read() + "\n" + DIVIDER)

def files_exist(list_of_files):
    """
    Returns False if any files in argument list of paths are missing.
    """
    for file in list_of_files:
        if not os.path.isfile(file):
            return False
    return True

def run_tests(hw, executable, output, diff=False):
    """
    Run an executable with various inputs and print the results to output.
    Args:
        hw (str): The homework being graded (e.g., "hw2")
        executable (str): Path to an executable file.
        output (obj): File to write results to.
        diff (:bool): Output as diff.
    """
    # the path to the input directory
    input_path = os.path.join(TEST_FILES_PATH_PREFIX, hw, "input")
    output_path = os.path.join(TEST_FILES_PATH_PREFIX, hw, "output")
    input_list = list(map(lambda x: input_path + "/" + x, os.listdir(input_path)))

    if not input_list:
        result = run(executable)
        if result == "__TIMEOUT__":
            output.write(TIMEOUT_MSG)
        else:
            with open(output_path + "/" +hw) as opf:
                op_string = opf.read()
            output.write("\n\nOUTPUT: " + hw + "\n\n")
            for line in result:
                output.write(line)
            if diff:
                output.write("\n\nDIFF: " + hw + "\n\n")
                for line in difflib.unified_diff(result.strip().splitlines(),
                                                 op_string.strip().splitlines(),
                                                 fromfile='Student Output',
                                                 tofile='Reference Output'):
                    output.write(line + '\n')
                output.write("\n\n")
    else:
        for input in input_list:
            result = run(executable, stdin=input)
            if result == "__TIMEOUT__":
                output.write(TIMEOUT_MSG)
            else:
                op = os.path.basename(os.path.normpath(input))
                with open(output_path + "/" + op) as opf:
                    op_string = opf.read()
                output.write("\n\nOUTPUT: " + op + "\n\n")
                for line in result:
                    output.write(line)
                if diff:
                    output.write("\n\nDIFF: " + op + "\n\n")
                    for line in difflib.unified_diff(result.strip().splitlines(),
                                                     op_string.strip().splitlines(),
                                                     fromfile='Student Output',
                                                     tofile='Reference Output',
                                                     lineterm=''):
                        output.write(line)
                    output.write("\n\n")
    output.write(DIVIDER)


################################################################################
# main
################################################################################

def main():
    parser = config_argparser()
    args = parser.parse_args()

    # the name of the homework to grade, e.g. hw1
    hw = args.homework

    # create / empty result directories for this hw
    results_dir = os.path.join(RESULTS_PATH_PREFIX, hw + "_results")
    student_files_dir = os.path.join(results_dir, "student_files")
    if os.path.isdir(results_dir):
        empty_dir(results_dir)
        empty_dir(student_files_dir)
    else:
        os.makedirs(student_files_dir)

    # get list of active students
    students = active_students(GRADE_JSON_PATH)

    # if unixname command line argument provided, only process specified student
    if args.unixname:
        students = [args.unixname]

    for student in students:
        output = open(os.path.join(results_dir, student), "a")

        output.write("\n\n")
        output.write(hw + "report for: " + student +"\n")
        output.write(DIVIDER)

        if not os.path.isdir(os.path.join(COURSE_DIR, student)):
            print("Error: Missing student directory (" + student + ").")
            continue

        if hw not in os.listdir(os.path.join(COURSE_DIR, student)) :
            output.write(MISSING_MSG)
            output.close()

        else:
            # make a directory for this student
            student_dir = os.path.join(student_files_dir, student)
            os.makedirs(student_dir)

            # path to executable (always named "main" for grading)
            student_exec_path = os.path.join(student_dir, "main")

            # collect paths to student's files based on required file doc
            required_files = get_rf_list(hw)
            student_src = []
            for f in required_files:
                student_src.append(os.path.join(COURSE_DIR, student, hw, f))

            # make sure all needed files are present
            if not files_exist(student_src):
                output.write(MISSING_MSG)
                continue

            check_submission_time(student_src, output, hw)

            # print student source code
            print_source(student_src, output)

            # compile student source
            gccflags = "-I" + os.path.join(COURSE_DIR, student, hw)
            if args.make:
                compile_result = True
                compile_str = run("make")
            if args.altmain:
                student_src.append(os.path.join(ALT_MAIN_PATH_PREFIX, hw + "_am.c"))
            if args.c99mode:
                compile_result, compile_str = compile(student_src, student_exec_path, gccflags + " -std=c99")
            else:
                compile_result, compile_str = compile(student_src, student_exec_path, gccflags)

            output.write(compile_str)
            output.write(DIVIDER)


            if args.notes:
                notes_path = os.path.join(COURSE_DIR, student, hw, "notes.txt")
                if os.path.isfile(notes_path):
                    print_source([os.path.join(COURSE_DIR, student, hw, "notes.txt")], output)
                else:
                    output.write("notes.txt file not found.\n")
                    output.write(DIVIDER)

            if compile_result:
                # successfully compiled, run program with test input
                run_tests(hw, student_exec_path, output, args.diff)

            output.write(get_gc_string(hw))

            output.close()

# END METHODS ##################################################################



if __name__ == '__main__':
    main()
