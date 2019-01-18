#!/usr/bin/python

import sys
import re
import json

def parse_read_summary(summary_path):
    read_summary_headers = []
    read_summary_lines = []
    # Basic approach to parsing text between two specific lines
    # described here: https://stackoverflow.com/a/7559542/780188
    with open(summary_path) as summary:
        for line in summary:
            if re.match("^Level", line):
                read_summary_headers = re.split("\s*,", line.rstrip())
                read_summary_headers = [
                    x.lower().replace(" ", "_") for x in read_summary_headers
                ]
                read_summary_headers = [
                    x.replace("%>=q30", "percent_greater_than_q30") for x in read_summary_headers
                ]
                break
        for line in summary:
            if re.match("^Total", line):
                read_summary_lines.append(re.split("\s*,", line.rstrip()))
                break
            read_summary_lines.append(re.split("\s*,", line.rstrip()))

    read_summary = []
    for line in read_summary_lines:
        read_summary_line_dict = {}
        for idx, header in enumerate(read_summary_headers):
            if header == 'level':
                read_summary_line_dict[header] = line[idx]
            elif header == 'intensity_c1':
                read_summary_line_dict[header] = int(line[idx])
            else:
                read_summary_line_dict[header] = float(line[idx])
        read_summary.append(read_summary_line_dict)
    
    return read_summary

#modular functions for detailed parse
def parse_file(file_path):
    list = []
    start = 0
    with open(file_path) as in_file:
        for line in in_file:
            if re.match("^Lane", line):
                start = 1
            if re.match("^Read", line) or re.match("^Extracted", line):
                start = 0
            if start == 1:
                list.append(build_lines(line))
    return list

#builds stripped list from line
def build_lines(line):
    header = re.split("\s*,", line.rstrip())
    header = [x.lower().replace(" ", "_").replace("/","_") for x in header]
    header = [x.replace("%>=q30", "percent_greater_than_q30") for x in header]
    return header

#structures list of data into lists containing lists for a read and the lanes of data
def struct_read(list):
    struct = []
    temp_list = []
    intial = False
    for line in list:
        if line[0] == "lane":
            struct.append(temp_list)
            temp_list = []
        temp_list.append(line)
    struct.append(temp_list)
    del struct[0]
    return struct

#transposes lists for a read and lanes of data to match header with lane values
def transpose(list_of):
    dict = {}
    index_list = []
    transpose = map(list, zip(*list_of))
    return transpose

#from a transposed list, creates dictionary from lists taking first list element as key
def struct_dict(list):
    dict = {}
    for line in list:
        key = line.pop(0)
        dict[key] = line 
    return dict

#create list of dictionaries from file path
def parse_read_summary_detail(file_path):
    list = []
    stage = struct_read(parse_file(file_path))
    for line in stage:
        list.append(struct_dict(transpose(line)))
    return list

def main():
    summary_path = sys.argv[1]
    #read_summary = parse_read_summary(summary_path)
    read_summary = parse_read_summary_detail(summary_path)
    print(json.dumps(read_summary))
    
if __name__ == '__main__':
    main()
