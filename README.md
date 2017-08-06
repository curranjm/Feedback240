# Feedback240

In an effort to learn Python while teaching a summer course (cs240), I wrote this grading tool for an introductory C course. Its scope and requirements are specific to my circumstances at the time, but I continue working on it as I learn about coding in Python, hopefully ending with a more widely applicable command line grading tool.

---

## Modules

There are three modules:  
### grade240  
 This module generates a directory containing grade reports for a specific homework assignment. The reports include the following information:  
* whether the code was submitted on time or not
* the student's source
* compilation output
* execution output
* comparison to expected execution output
* a grading criteria (to be adjusted by grader based on above information)

### notify240  
 This module emails the completed grade reports to all active students.

### status240  
 This module produces a status report for each student based on their homework, quiz, and exam grades as of the day it is executed.

---

## Requirements

Feedback240 assumes the following:

* Each student is a user on a unix-like system
* There is a course directory containing student directories named based on
students usernames
* Students save their work in folders named "hw1", "hw2", etc.
* The grader maintains a gradebook json file to track student grades

---

## Usage

Usage of Feedback240 evolved throughout the summer session as I wrote new assignments and dealt with different grading requirements. Currently, the workflow is as follows:

1. Create the support files for the assignment and place them in the support_files directory. Support files include:
 * an optional main.c file to drive student functions (otherwise expects this to be provided by students)
 * a required files file identifying the source files the student must provide
 * optional input files for testing
 * a required file with expected output
 * the grading criteria for the homework

2. Invoke grade240 with the homework being graded and any options:  
 ./grade240 hw1

 Options include whether or not to use an alternate main.c to run the student code, whether to include a diff in the output, whether to compile using a makefile, whether or not there is a notes.txt file expected for this homework, and any special options to compile with (e.g., c99 mode).

 Providing a specific student's username at the command line allows generation of grading results for a single student.

3. Invoke notify240 with the homework being graded to send results to all active students in the class:  
 ./notify240 hw1

 (Note that notify can also be invoked for one student at a time.)
