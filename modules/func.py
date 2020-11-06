import json
import os
from fractions import Fraction
from pathlib import Path
import shutil

import subprocess
from html.parser import HTMLParser

from modules import PROJ_CONST as PR
import pandas
import csv
from PyPDF2 import PdfFileReader


def cleanup():
    if os.path.exists(PR.DIR_PROJECT) and os.path.isdir(PR.DIR_PROJECT):
        shutil.rmtree(PR.DIR_PROJECT)
        print("Old project flies deleted.")


def create_project():
    # create directory for the project
    Path(PR.DIR_PROJECT).mkdir(parents=True, exist_ok=True)
    Path(PR.DIR_TABULATED_CSV).mkdir(parents=True, exist_ok=True)
    # Path(PR.DIR_PRODUCT_TABLES).mkdir(parents=True, exist_ok=True)
    # Path(PR.DIR_TREATED_ROWS).mkdir(parents=True, exist_ok=True)

    if os.path.exists(PR.DIR_PROJECT) and os.path.isdir(PR.DIR_PROJECT):
        print(f"New project directory {PR.DIR_PROJECT} created")
    else:
        print(f"New project directory {PR.DIR_PROJECT} creation FAILED")
#
#
# class MyHtmlParser(HTMLParser):
#     def __init__(self):
#         HTMLParser.__init__(self)
#         self.page_data_set = set()  # creates a new empty set to  hold data items from the html
#         self.page_data_list = []
#
#     def handle_data(self, data):
#         if "font-family" not in data:
#             data = " ".join(data.split())
#             self.page_data_set.add(data)
#             self.page_data_list.append(data)
#
#
# def convert_to_html(infilename, first, last):
#     # run pdftohtml https://www.xpdfreader.com/pdftohtml-man.html
#     success = True
#     command = "pdftohtml -q -f {} -l {} {} {}".format(first, last, infilename, PR.DIR_XPDF).split()
#     pdftohtml_process = subprocess.run(command)  ## run executes command and waits for it to finish
#
#     # signal error from pdftohtml process
#     if pdftohtml_process.returncode:
#         print(f"pdftohtml return code: {pdftohtml_process.returncode}")
#         success = False
#
#     # cleanup unnecessary files
#     files_created = set(os.listdir(PR.DIR_XPDF))
#     mask_to_remove = [".png", ".ttf", "index.html"]
#     for f in files_created:
#         for m in mask_to_remove:
#             if m in f:
#                 os.remove("{}{}".format(PR.DIR_XPDF, f))
#
#     return success
#

def determine_n_pages(infilename):
    """determine number of pages in the infile"""
    with open(infilename, 'rb') as fl:
        reader = PdfFileReader(fl)
        return reader.getNumPages()


def ask_for_filename(args):
    infilename = None
    while True:
        infilename = input("Enter the name of pdf file: ")
        if ".pdf" not in infilename and not len(infilename.split()) == 0:
            infilename += ".pdf"
        if not infilename:
            continue
        if not os.path.exists(infilename) or not os.path.isfile(infilename):
            print(f"{infilename} does not exist.\n ")
        else:
            break
    return infilename


def ask_for_n_pages(total, start):
    n = None
    while True:
        ans = input("How many pages to process: ").upper()
        if ans == "ALL":
            n = "ALL"
            break
        elif ans.isdigit() and (int(ans) + start - 1 <= total):
            n = int(ans)
            break
        else:
            print(f"Max number: {total - start + 1}")
    return n


def ask_for_starting_page(total_pages):
    p = None
    while True:
        ans = input(f"Enter the starting page number: ")
        if ans.isdigit() and int(ans) <= total_pages:
            p = int(ans)
            break
        else:
            print(f"Invalid number")
    return p


# # ==================  functions for tf.py  === table filler ==============
#
#
# def read_to_dict(source_path):
#     source_dict = {}
#
#     if os.path.exists(source_path) and os.path.isfile(source_path):
#         # read the csv file call it csvfile
#         with open(source_path, newline='') as csvfile:
#             dict_reader_object = csv.DictReader(csvfile, dialect='excel')  # returns reader object that is an iterator
#             list_of_csv_rows = list(dict_reader_object)
#             source_dict = {}  # to contain data from product_table.csv file
#             for key in dict_reader_object.fieldnames:
#                 source_dict[key] = []
#                 for row in list_of_csv_rows:
#                     source_dict[key].append(row[key])
#     else:
#         print(f"Not found: {source_path}")
#
#     return source_dict
#
#
# def export_dict(dictionary, filename):
#     df = pandas.DataFrame(dictionary)
#     df.to_csv(filename, index=False)
#

def export_dict_ragged_to_csv(d, filename):
    """ export ragged dictionary in csv"""
    with open(filename, "w", newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(d.keys())
        max_len = 0  # max len of list in a key
        for v in d.values():
            if len(v) > max_len:
                max_len = len(v)
        rows = []
        for i in range(max_len):
            row = []
            for key in d.keys():
                if i < len(d[key]):
                    item = d[key][i]
                else:
                    item = ''
                row.append(item)
            rows.append(row)

        writer.writerows(rows)


def print_dict(d):
    print(list(d.keys()))
    max_len = 0  # max len of list in a key
    for v in d.values():
        if len(v) > max_len:
            max_len = len(v)

    for i in range(max_len):
        row = []
        for key in d.keys():
            if i < len(d[key]):
                item = d[key][i]
            else:
                item = ''
            row.append(item)
        print(row)





def read_json_data(json_file_name):
    """ :returns list of dictionaries correspoinding to json objects """
    with open(json_file_name, 'r') as json_file:
        data = json.load(json_file)

    return data


def extract_page_data_from_json_data(json_data, pagenumber):
    """ :param json_data is a list of dictionaries containing selections from the whole pdf document
    :param pagenumber is current page number
    :returns page_data - a list of dictionaries containing keys: page, extraction_method, x1, x2, y1, y2, width, height
         which is relevant to the pagenumber only"""
    page_data = [data for data in json_data if data["page"] == pagenumber]
    return page_data


def write_line_list_to_csv(aList, filename):
    """ writes lsit of lines into csv filename"""
    # for testing
    # print("write_line_list_to_csv:")
    # for row in aList:
    #     print(row)

    with open(filename, "w", newline='', encoding='utf-8') as f:
        wr = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        wr.writerows(aList)


def convert_dataframe_tolist_of_lines(df):
    """ :param df dataframe corresponding to one selection
    :returns lines_list that represents selection"""
    lines_list = [list(df.columns), *df.values.tolist()]  # list of lines representing current selection
    return lines_list


def fract2float(num):
    """ converts fractional inch notation with '-' delimiting inch to decimal inch notation
    :return float representation """

    # Convert the inch to a real and frac part  Note it is assumed that the real and frac
    # parts are delimited by '-'
    result = 0

    try:
        real, x, frac = num.rpartition("-")
        if real == '':
            real = 0
        result = int(real)
        result += Fraction(frac)
    except ValueError:
        None
    return float(result)


def fract_dim_to_float_dim(dim):
    """ converts fractional inch dimensions into decimal inch dimensions
    :return string representation"""
    left, x, right = dim.rpartition('x')
    left = str(fract2float(left))
    right = str(fract2float(right))
    return left + 'x' + right

def dim_equals(dim1, dim2):
    """ :param dim1 dim2 is a float representation of dimension delimited by 'x'
    :return true if dim1 equals dim2, false otherwise """
    left1, x, right1 = dim1.rpartition('x')
    left2, x, right2 = dim2.rpartition('x')
    res  = False
    try:
        res =  float(left1)==float(left2) and float(right1)==float(right2)
    except ValueError:
        None

    return res