#! /usr/bin/env python3.5

import argparse
import json
from os import path, getcwd
from config.settings240 import *
import smtplib

# in test mode no email is sent -- email contents are sent to stdout
TEST_MODE = True

# METHODS ######################################################################

def send_mail(grader_email, student_email, message):
    """
    Sends a grade email to the student from the grader.
    Args:
        grader_email (str): the "from" email address
        student_email (str): the "to" email address
        message (str): the email as a string formatted for smtlib
    """
    if TEST_MODE:
        print(message)
    else:
        smtp_obj = smtplib.SMTP(SMT_SERV, SMT_PORT)
        smtp_obj.starttls()
        smtp_obj.ehlo()
        smtp_obj.login(SMT_USER, SMT_PASS)

        try:
            smtp_obj.sendmail(grader_email, student_email, message)
        except smtplib.SMTPException:
            print("Failed to send email to: " + student_email)
        finally:
            smtp_obj.quit()


def grade_report(path_to_report):
    """
    Takes a path to a grade report file and returns it as a string.
    If the grade file does not exist, returns a missing file message.
    """
    if path.isfile(path_to_report):
        with open(path_to_report,'r') as f:
            return f.read() + "\n"
    else:
        print("Could not find: " + path_to_report)
        print("Sending missing file message.\n")
        return MISSING_MSG

def build_message(student, hw):
    """
    Assemble a message string in the format required by smtplib.
    Args:
        student (obj): a student grade dict generated from a json file
    Returns:
        str: The formatted message string.
    """
    student_email = student + "@cs.umb.edu"
    body = ""
    body += ("Sent to: " + student_email + "\n"
            + "Course: " + COURSE_NAME + "\n"
            + "Assignment: " + hw + "\n\n"
            + DIVIDER)
    body += grade_report(path.join(RESULTS_PATH_PREFIX, hw + "_results", student))
    body += ("\n" + DIVIDER
            + "\n\nIf you received this message in error or have questions about your grade,\n"
            + "reply to this message or contact me at: " + GRADER_EMAIL + ".\n"
            + "\n" + DIVIDER)
    # assemble the message in the format required by smtplib
    message = ("To: " + student_email + "\r\n" +
               "Subject: " + COURSE_NAME + ", " + hw + " Grade\r\n\r\n" +
               body)
    return message.encode('utf-8')

def config_argparser():
    """
    Sets up command line options using argparse and returns the argparse
    argument parser object.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("homework",
                        help="The homework whose grade to send (e.g., hw1)")
    parser.add_argument("-u",
                        "--unixname",
                        help="Send grade to the specified unix name only")
    return parser


def main():
    parser = config_argparser()
    args = parser.parse_args()

    # the homework whose grade to send (e.g., hw1)
    hw = args.homework

    with open(GRADE_JSON_PATH) as data_file:
        data = json.load(data_file)

    if args.unixname:
        send_mail(GRADER_EMAIL,
                  args.unixname + "@cs.umb.edu",
                  build_message(args.unixname, hw))
        print("\nGrade email sent to " + args.unixname + ".\n")
    else:
        for student in data:
            if student["withdrawn"] != 1:
                send_mail(GRADER_EMAIL,
                          student["unixName"] + "@cs.umb.edu",
                          build_message(student["unixName"], hw))
                print(hw + " grade sent to " + student["unixName"])
        print("\nGrade emails sent to " + str(len(data)) + " students.\n")


# END METHODS ##################################################################


if __name__ == '__main__':
    main()
