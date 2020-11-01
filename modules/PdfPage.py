import csv

import tabula

from modules.PageProductTable import PageProductTable
from modules import PROJ_CONST as PR
from modules import PDF_CONST as PFC
from modules.PdfLine import PdfLine
from modules.func import *
from pprint import pprint


class PdfPage:
    """ converts Pdf page to csv, creates a list of PdfLine objects for each line and passes it to PdfProductTable and PdfColorTable"""

    def __init__(self, infilename, pagenumber, coordinates):
        self.infilename = infilename
        self.pagenumber = pagenumber
        self.coordinates = coordinates
        print("page:", self.pagenumber)  # print page number while creating
        self.midfilename = '{}tabulated_{}.csv'.format(PR.DIR_TABULATED_CSV, self.pagenumber)
        # read all rows of the current page in a list of lists

        # passed to the PageProductTable
        self.selection_dataframes = self.read_with_json_tabula(self.infilename, self.pagenumber, self.coordinates)

        # # would work if tables were recognized with proper header but there are plenty of small tables each with its own tiltle
        # self.selection_dicts = self.convert_list_of_dataframes_to_list_of_dict(self.selection_dataframes)
        # print("dicts")
        # for my_dict in self.selection_dicts:
        #     print_dict(my_dict)
        #     print("")
        #     pprint(my_dict)
        #     print("")

        # # write to list of template rows for testing and tabulated csv only
        self.list_of_page_tabula_rows = self.convert_list_of_dataframes_tolist_of_lines(self.selection_dataframes)
        # # print for testing
        # for my_df in self.selection_dataframes:
        #     selection_lines = self.convert_list_of_dataframes_tolist_of_lines([my_df])
        #     for line in selection_lines:
        #         print(line)
        #     print("")

        # #  represent selections as lists of lines
        # self.selections_as_line_lists = self.convert_list_of_dataframes_to_selection_lines(self.selection_dataframes)



        # self._contains_color_table = self.contains_color_table()

        # constructs list of PdfLine objects
        # for each template row make an object that contains methods that can fetch attributes

        # self._pdf_line_list = [PdfLine(line) for line in self.list_of_page_tabula_rows]

        # self._page_contains_color_info = self.page_contains_color_info()

        self._color_list = None
        # # below initialise the color list
        # if self._contains_color_table:
        #     self._color_list = self.extract_color_list_with_tabula_lattice()
        # print("color_list", self._color_list)
        # print("contains color table", self._contains_color_table)

        # moved creation of product tables to the PdfDoc class
        self._product_table = None  # main table of the page containing its products together with all attributes

        # export tabulated csv for current pagenumber
        write_line_list_to_csv(self.list_of_page_tabula_rows, self.midfilename)

    # def contains_color_table_header(self):
    #     """ :returns true if guessed rows contain "- COLORS" which is usually in color table header"""
    #     contains = False
    #     for row in self.list_of_page_tabula_rows:
    #         row = [str(item) for item in row]
    #         row_string = "".join(row)
    #         if "Colors" in row_string:
    #             contains = True
    #     return contains

    # def contains_color_table(self):
    #     """ :returns true if current page contains separate color table on the bottom of the page """
    #     contains = self.contains_color_table_header()
    #     return contains

    def create_product_table(self, external_color_list=None):
        # print(self.pagenumber, "PdfPage._page_contains_color_info", self._page_contains_color_info)
        # print(self.pagenumber, "PdfPage._color_list", self._color_list)
        # print(self.pagenumber, "external color list", external_color_list)
        # print(self.pagenumber, "_contains_color_table", self._contains_color_table)
        # print(self.pagenumber, "contains_color_table_header", self.contains_color_table_header())
        # ####### print(self.pagenumber, "contains_color_note", self.contains_color_note())

        # if self._page_contains_color_info or self._color_list:  # color in the product row or in a table below on the same page

        # was passed selected_areas=self.selections_as_line_lists
        self._product_table = PageProductTable(page_number=self.pagenumber,
                                               selection_dfs=self.selection_dataframes)
        # else:  # page doesn't contin color info in itself
        #     self._product_table = PageProductTable(self._pdf_line_list, self.list_of_template_rows, self.pagenumber,
        #                                            external_color_list)

    def read_with_json_tabula(self, infilename, pagenumber, json_page_data):
        """
        :return list of dataframes representing all selections on the current page
        :param json_page_data is a list of dictionaries containing keys: page, extraction_method, x1, x2, y1, y2, width, height
         which is relevant to the current page only"""
        selection_coordinates = [(data["y1"], data["x1"], data["y2"], data["x2"]) for data in
                                 json_page_data]  # list of tuples of $y1,$x1,$y2,$x2 coordinates for this page
        selection_coordinates.sort(key=lambda selection: selection[1])  # sort by x1
        selection_coordinates.sort(key=lambda selection: selection[0])  # sort by y1
        dict_list = []  # list of rows representing current page
        # print("read_with_json_tabula:")
        for tuple in selection_coordinates:
            df_list = tabula.read_pdf(
                input_path=infilename, output_format="dataframe", pages=pagenumber,
                stream=True, lattice=False, multiple_tables=True, guess=True,
                area=tuple,
            )
            df = df_list[0]  # the dictionary is on a singleton list
            df = df.fillna('')  # nan fields are substituted by empty string

            # # for testing
            # export_dict_ragged_to_csv(df.to_dict(), self.midfilename)
            # convert dataframe to list of rows including header

            dict_list.append(df)
        return dict_list

    def convert_dataframe_tolist_of_lines(self, df):
        """ :param df dataframe corresponding to one selection
        :returns lines_list that represents selection"""
        lines_list = [list(df.columns), *df.values.tolist()]  # list of lines representing current selection
        return lines_list

    def convert_list_of_dataframes_tolist_of_lines(self, df_list):
        """ :param df_list - list of dataframes
            :return list of lists corresponding to list of lines
        """
        ls = []
        for df in df_list:
            ls += self.convert_dataframe_tolist_of_lines(df)
        return ls

    def convert_list_of_dataframes_tolist_of_dict(self, df_list):
        """ :param df_list - list of dataframes
            :return list of dict corresponding to list of lines
        """
        ls = []
        for df in df_list:
            ls.append(df.to_dict())
        return ls

    def convert_list_of_dataframes_to_selection_lines(self, df_list):
        """ :param df_list - list of dataframes
        :return list of lists representing selections on the current page"""
        selectios_ = []
        for my_df in df_list:
            selection_lines = self.convert_list_of_dataframes_tolist_of_lines([my_df])
            print(selection_lines)
            selectios_.append(selection_lines)
        # print("selections as lines:")
        # print(selectios_)
        return selectios_


