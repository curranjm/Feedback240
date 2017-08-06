#! /usr/bin/env python3.5

import argparse
import heapq
import json
from grade240 import CS240_DIR, JSON_PATH, DIVIDER, empty_dir, active_students
import os
import time


# CONSTANTS ####################################################################

# END CONSTANTS ################################################################


# METHODS ######################################################################

################################################################################
# misc helpers
################################################################################

def get_default_counts(student):
    result = {"hw":0, "ex":0, "qz":0}
    for item in student.keys():
        if "hw" in item:
            result["hw"] += 1;
        elif "ex" in item:
            result["ex"] += 1;
        elif "qz" in item:
            result["qz"] += 1;
    return result

def get_student(data, unix):
    """
    Extract a particular student from JSON data object, based on unix name.
    Args:
        data (obj): dictionary based on the json score document
        unix (str): name of the student to return
    Returns:
        obj: a dict mapping homeworks/exams/quizzes to their max scores
    """
    for student in data:
        if student["unixName"] == unix:
            return student

def get_hw_info(student, hw, max_scores):
    """
    Calculate the homework average and an explanation.
    Args:
        student (obj): A JSON student object with grade information.
        hw (int): The number of homeworks to look at.
        max_scores (obj): dict mapping hw/exam/quiz to max score
    Returns:
        int: homework average, rounded to nearest int
        str: student homework grade string
    """
    total = 0
    report = ("Homework\n" + DIVIDER)
    for i in range(1, hw + 1):
        suffix = str(i).rjust(2, '0')
        sub = round((student["hw" + suffix] * 100) / max_scores["hw" + suffix]);
        total += sub
        report += ("  hw" + suffix + ": " +
                   str(student["hw" + suffix]).rjust(2, ' ') + " / " + str(max_scores["hw" + suffix]) +
                   " (" + str(sub) + ")\n")
    avg = round(total / hw)
    report += "hw average: " + str(avg) + "\n" + DIVIDER
    return (avg, report)

def get_ex_info(student):
    """
    Calculate the exam average and an explanation.
    Args:
        student (obj): A JSON student object with grade information.
    Returns:
        int: exam average, rounded to nearest int
        str: student exam grade string
    """
    heap = []
    report = ("Exams\n" + DIVIDER)
    for i in range(1, 4):
        suffix = str(i).rjust(2, '0')
        heap.append(student["ex" + suffix])
        report += "  ex" + str(i) + ": " + str(student["ex" + suffix]).rjust(3, ' ') + "\n"
    heapq.heapify(heap)
    avg = round( (heap[1] + heap[2]) / 2 )
    report += "exam average (best 2): " + str(avg) + "\n" + DIVIDER
    return (avg, report)

def get_qz_info(student):
    """
    Calculate the quiz average and an explanation.
    Args:
        student (obj): A JSON student object with grade information.
    Returns:
        int: quiz average, rounded to nearest int
        str: student quiz grade string
    """
    report = ("Quizzes\n" + DIVIDER)
    total = 0
    for i in range(1, 4):
        suffix = str(i).rjust(2, '0')
        total += student["qz" + suffix]
        report += "  qz" + str(i) + ": " + str(student["qz" + suffix]).rjust(3, ' ') + "\n"
    avg = round(total / 3)
    report += "quiz average: " + str(avg) + "\n" + DIVIDER
    return (avg, report)






################################################################################
# Generate a grade report for selected student(s).
################################################################################
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u",
                        "--unixname",
                        help="Generate status of the specified unix name only")
    parser.add_argument("-a",
                        "--assignments",
                        type=int,
                        help="The number of homeworks that have been graded.")
    parser.add_argument("-e",
                        "--exams",
                        type=int,
                        help="The number of exams that have been graded.")
    parser.add_argument("-q",
                        "--quizzes",
                        type=int,
                        help="The number of quizzes that have been graded.")
    args = parser.parse_args()


    # create / empty result directories for this hw
    results_dir = os.path.join(os.getcwd(), "status" + time.strftime("%m-%d-%y"))
    if os.path.isdir(results_dir):
        empty_dir(results_dir)
    else:
        os.mkdir(results_dir)

    with open(JSON_PATH) as data_file:
        data = json.load(data_file)

    # get default counts of hw, exams, quizzes
    counts = get_default_counts(data[0])
    if args.assignments:
        counts["hw"] = args.assignments
    if args.exams:
        counts["ex"] = args.exams
    if args.quizzes:
        counts["qz"] = args.quizzes

    # # get list of active students
    # students = active_students(JSON_PATH)

    # get max_score object
    max_scores = get_student(data, "max_score")

    # if unixname command line argument provided, only process specified student
    if args.unixname:
        data = {get_student(data, args.unixname)}

    raw_grades = {}

    for student in data:
        if (student['withdrawn'] != 1):
            output = open(os.path.join(results_dir, student['unixName']), "a")
            output.write("\n\n")
            output.write("Status report for: " + student['unixName'] +"\n")
            output.write(DIVIDER)
            hw_grade, hw_report = get_hw_info(student, counts["hw"], max_scores)
            output.write(hw_report)
            ex_grade, ex_report = get_ex_info(student)
            output.write(ex_report)
            qz_grade, qz_report = get_qz_info(student)
            output.write(qz_report)
            raw_final = round(hw_grade * .3 + ex_grade * .6 + qz_grade * .1)
            raw_grades[student["unixName"]] = raw_final
            output.write("Raw final grade: " + str(raw_final))
            output.close()

    report_path = os.path.join(results_dir, "final_report.txt");
    rp = open(report_path, 'w')
    for grade in sorted(raw_grades, key = raw_grades.get):
        rp.write(grade.ljust(15, '.') + " " + str(raw_grades[grade]) + "\n")
    rp.close()


# END METHODS ##################################################################



if __name__ == '__main__':
    main()
