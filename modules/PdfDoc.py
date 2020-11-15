import pandas

from modules import PROJ_CONST as PR, PDF_CONST as PFC
from modules.PdfPage import PdfPage
from modules.func import *
from bedroser import DOC_SELECTIONS_COORDINATES


class PdfDoc:
    """ manages a list of PdfPage objects"""

    def __init__(self, in_file_name, pickled_data, config_dict, se_range, page_start=1, n_pages=1):
        """by default grabs the first page only"""
        self.pickled = pickled_data
        self.config_dict = config_dict
        self.se_range = se_range
        self.page_start = page_start
        self.n_pages = n_pages
        self.in_file_name = in_file_name
        self._pages = None
        self.__all_pages_product_dict = {}  # dictionary that will hold the items of all product tables
        self.jsondata = read_json_data(DOC_SELECTIONS_COORDINATES)

    def export_cumulative_dict(self, filename):
        df = pandas.DataFrame(self.__all_pages_product_dict)
        df.to_csv(filename, index=False)

    def create_pages(self):
        _pages = [PdfPage(infilename=self.in_file_name,
                          pickle_data=self.pickled,
                          config_d=self.config_dict,
                          pagenumber=i,
                          se_range=self.se_range,
                          coordinates=extract_page_data_from_json_data(json_data=self.jsondata, pagenumber=i)) for i in
                  range(self.page_start, self.page_start + self.n_pages)]  # list of PdfPage objects
        self._pages = _pages

    def create_product_tables(self):
        self._pages.reverse()
        self._pages[0].create_product_table()  # create table of the last page
        p_t = self._pages[0].product_table
        p_t.build_table()  # push attributes to the dict
        ext_pckg = p_t.packaging_selections
        ext_series = p_t._series_name
        #  create tables of the rest of the pages (in reverse order)
        for i in range(1, len(self._pages)):
            self._pages[i].create_product_table()
            p_t = self._pages[i].product_table
            p_t.build_table(ext_pckg, ext_series)  # push attributes to the dict
            if p_t.packaging_selections:
                ext_pckg = p_t.packaging_selections
                ext_series = p_t._series_name
        self._pages.reverse()

        # self._pages[len(self._pages) - 1].create_product_table()  # ceate last product table with no external color list

    def construct_cumulative_dict(self):
        self.__list_of_all_product_dicts = [page.product_table.get_products() for page in self._pages]

        # construct cumulative dictionary
        for key in PFC.PRODUCT_TABLE_FIELDS:
            self.__all_pages_product_dict[key] = []
            for item in self.__list_of_all_product_dicts:
                self.__all_pages_product_dict[key] += item[key]

        # print(f"cumulative dict: {self.__list_of_all_product_dicts}")

    # # # =================== Not used  =======================
    # # def create_decending_stack_of_pages(self):
    # #     """ :returns a stack onf PdfPage objects with greatest page number first"""
    # #     range_start = self.page_start
    # #     range_end = self.page_start + self.n_pages
    # #
    # #     _stack = []
    # #
    # #     index = range_end - 1
    # #     while index >= range_start:
    # #         page = PdfPage(self.in_file_name, pagenumber=index)
    # #         _stack.append(page)
    # #         index -= 1
    # #     return _stack
    # #
    # # def construct_product_tables (self, the_stack):
    # #     range_start = self.page_start
    # #     range_end = self.page_start + self.n_pages
    # #
    # #     index = range_end - 1
    # #
    # #     for i in range(len(the_stack)):
    # #         if the_stack[i]._contains_color_table:
    # #             the_stack[i].create_product_table()
    # #         # else:

    def collect_selection_dfs(self):
        """ :return a dictionary {pagenumber: [df1, df2 ...]}"""
        all_page_dfs = {}
        for page in self._pages:
            all_page_dfs[page.pagenumber] = page.selection_dataframes
        return all_page_dfs
