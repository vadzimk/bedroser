import csv

import tabula

from modules.PageProductTable import PageProductTable
from modules import PROJ_CONST as PR
from modules import PDF_CONST as PFC
from modules.PdfLine import PdfLine
from modules.func import *
from pprint import pprint


# from bedroser import list_of_pages_with_doubled_rows


class PdfPage:
    """ converts Pdf page to csv, creates a list of PdfLine objects for each line and passes it to PdfProductTable and PdfColorTable"""

    def __init__(self, infilename, pickle_data, config_d, pagenumber, se_range, doubled_rows_pagens, coordinates):
        self.infilename = infilename
        self.config_d = config_d
        self.pagenumber = pagenumber
        self.doubled_rows_pagens = doubled_rows_pagens
        self.is_se = self.is_in_se_range(se_range, pagenumber)
        self.coordinates = coordinates
        print(f"page:", self.pagenumber)  # print page number while creating
        self.midfilename = '{}tabulated_{}.csv'.format(PR.DIR_TABULATED_CSV, self.pagenumber)
        # read all rows of the current page in a list of lists

        # passed to the PageProductTable
        pickled_dfs = self.read_pickled_data(pickle_data)
        if pickled_dfs:
            self.selection_dataframes = pickled_dfs
            # print("pickled_df------s", pickled_dfs)
        else:
            # print("no data")
            self.selection_dataframes = self.read_with_json_tabula(self.infilename, self.pagenumber, self.coordinates)

        # # write to list of template rows for testing and tabulated csv only
        self.list_of_page_tabula_rows = self.convert_list_of_dataframes_tolist_of_lines(self.selection_dataframes)

        # moved creation of product tables to the PdfDoc class
        self.product_table = None  # main table of the page containing its products together with all attributes

        # export tabulated csv for current pagenumber
        # write_line_list_to_csv(self.list_of_page_tabula_rows, self.midfilename)

    def create_product_table(self):

        self.product_table = PageProductTable(
            conf_d=self.config_d,
            page_number=self.pagenumber,
            is_se=self.is_se,
            selection_dfs=self.selection_dataframes)

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

        column_coordinates = None

        if pagenumber in self.doubled_rows_pagens:
            column_coordinates = PFC.COLUMN_X_COORDINATES_104_or106

        for c_tuple in selection_coordinates:
            df_list = tabula.read_pdf(
                input_path=infilename, output_format="dataframe", pages=pagenumber,
                stream=True, lattice=False, multiple_tables=True, guess=True,
                area=c_tuple, encoding='utf-8', columns=column_coordinates
            )
            try:
                df = df_list[0]  # the dictionary is on a singleton list
                df = df.fillna('')  # nan fields are substituted by empty string

                dict_list.append(df)
            except IndexError:
                pass
                # print(f"No selections on page {pagenumber}")
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
            # print(selection_lines)
            selectios_.append(selection_lines)
        # print("selections as lines:")
        # print(selectios_)
        return selectios_

    def is_in_se_range(self, se_range, pagenumber):
        s1, s2 = se_range
        is_se = False
        if s1 and s2:  # are not None
            is_se = pagenumber in range(s1, s2 + 1)
        return is_se

    def read_pickled_data(self, pickled):
        """ :param pickled a list of dictionaries {pagenumber: list_of_selections} or an empty list
        :return list of dataframes representing all selections on the current page"""
        return pickled.get(self.pagenumber)
