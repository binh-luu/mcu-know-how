# MISRA-C checker - main entry point

import os
import re
import csv
import sys
import shutil
import subprocess

def main(codeCheckFileName):

    # get 'cppcheck' command path with shutil.which
    cppcheck_command_path = shutil.which('cppcheck')

    # check cppcheck command path is exist or not
    if (cppcheck_command_path is None):
        print('Error: cppcheck command is not found')
        sys.exit(1)

    cppcheck_path = 'cppcheck-main'

    # define ruleFileName
    ruleFileName = 'misrac-2012.txt'

    # define cppcheck command
    # command format is cppcheck --dump {codeCheckFileName} {cppcheck_path}/addons/misra.py --rule-texts=misrac-2012.txt {codeCheckFileName}.dump
    cppcheck_command = '{} --dump {}'.format(cppcheck_command_path, codeCheckFileName)

    # exec cppcheck command and get command standard output
    cppcheck_result = subprocess.run(cppcheck_command, shell=True, capture_output=True, text=True).stdout

    # misra command format is 'python3 {cppcheck_path}/addons/misra.py --rule-texts={ruleFileName} {codeCheckFileName}.dump'
    misra_command = 'python3 {}/addons/misra.py --rule-texts={} {}.dump'.format(cppcheck_path, ruleFileName, codeCheckFileName)

    # exec misra_command command and get command standard output (both stdout and stderr)
    result = subprocess.run(misra_command, shell=True, capture_output=True, text=True)
    misra_result = result.stdout + result.stderr

    # ------------------------------------------------------------------
    # Parse misra_result and write violations to a CSV report.
    # CSV columns: File, Line, Column, Rule ID, Rule Category, Description
    # ------------------------------------------------------------------
    # csv_file_name = codeCheckFileName + '.csv'
    report_path = 'report'
    base_name = os.path.basename(codeCheckFileName)
    csv_file_name = os.path.join(report_path, '{}.csv'.format(base_name))
    with open(csv_file_name, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['File', 'Line', 'Column', 'Rule ID', 'Rule Category', 'Description'])

        # Process misra_result line by line - only lines starting with '[' are violations
        for violation_line in misra_result.split('\n'):
            violation_line = violation_line.strip()
            if not violation_line or not violation_line.startswith('['):
                continue

            # pattern: [file:line] (cppcheck_severity) description (misra_severity) [misra-c2012-X.Y]
            match = re.match(r'\[[^\]]+\]\s*\(([^)]+)\)\s*(.*)\s*\(([^)]+)\)\s*\[misra-c2012-([0-9.]+)\]', violation_line)
            if match:
                # Extract file and line number using separate simple regexes
                file_path = re.search(r'\[([^:]+):', violation_line).group(1)
                line_no = re.search(r':(\d+)\]', violation_line).group(1)

                # Groups: 1=cppcheck_sev, 2=description, 3=misra_sev (rule category), 4=rule_id
                cppcheck_severity = match.group(1)
                description = match.group(2).strip()
                rule_category = match.group(3)  # This is the Rule Category (Mandatory/Advisory/Required)
                rule_id = match.group(4)
                # misra.py stdout does not contain a column number
                csv_writer.writerow([file_path, line_no, '', rule_id, rule_category, description])

    # print misra_result
    print(misra_result)
    if "MISRA rules violations found" in misra_result:
        print("'{}' has MISRA rules violations\n".format(codeCheckFileName))
        return 1
    return 0

if __name__ == '__main__':
    # check argc is 2 or not
    if (len(sys.argv) < 2):
        print('usage: python3 main.py <c or cpp file path> ...')
        sys.exit(1)

    exit_status = []
    # call main function
    for i in range(0, len(sys.argv)):
        codeCheckFileName = sys.argv[i]
        if i > 0:
            exit_status.append(main(codeCheckFileName))

    for status in exit_status:
        if status != 0:
            print("fix some MISRA rules violations")
            sys.exit(1)
    sys.exit(0)