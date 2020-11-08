import functools
import re
from operator import attrgetter

import pandas

import modules.PDF_CONST as PFC
from modules import PROJ_CONST as PR
from modules.PdfLine import PdfLine
from modules.Selection import Selection
import csv
from pprint import pprint



class PageProductTable:
    """ contains products in a dictionary """

    def __init__(self, conf_d, page_number, selection_dfs):
        self._pagenumber = page_number
        self._config = conf_d # config dict from TARGET_CONFIG.csv
        self._selection_dfs = selection_dfs
        self.selection_objects = [Selection(df) for df in selection_dfs]
        self.set_selection_types()  # init selection types

        # self.lines = lines
        # print("guessed_rows")
        # for row in guessed_rows:
        #     print(row)
        # self.guessed_rows_strings = [self.join_list_items(item) for item in
        #                              guessed_rows]  # joins guessed rows and retrurns a list of strings
        # print("guessed_strings:")
        # for string in self.guessed_rows_strings:
        #     print(string)
        # # print("---tabulalines:")
        # # for line in lines:
        # #     print(line._tabula_line)
        # print("__ end")
        self.colors = None  # for testing
        self.description = None

        self.__products = {key: [] for key in
                           PFC.PRODUCT_TABLE_FIELDS}  # dictionary that will hold the items of the table
        #  fields of the csv data frame:
        self._series_name = None
        self._group = None
        self._subgroup = None  # subgroup is like "BULLNOSE"
        self._vendor_code = None
        self._item_size = None
        self._item_color = ''
        self._pieces_per_carton = None  # after testing change default value to 1
        self._units_of_measure = None
        self._unit_price = None
        self._sf_per_ctn = None
        self._ctn_per_plt = None

        # supplemental properties
        self.color_areas = []  # contains Color_area objects that are pushed as the build_table is running
        self.reset_color_areas = False  # gets True when Stock selection is encountered, the next color area encountered will set all color areas in self.color_areas used property to True

        self.packaging_selections = self.collect_packaging_selections()  # a list of Packaging_selection objects of current page that is fixed by the time  build_table is called

        print("packaging_selections")
        for sel in self.packaging_selections:
            print(sel)

        self.group_prefix = ''  # represents category prefix of subgroup
        self.contains_panel = False


        # print("num pack sel", len(self.packaging_selections))

        # self.build_table()  # put products in the dictionary

        # TODO keep this
        # export product table as csv
        # df = pandas.DataFrame(self.__products)
        # df.to_csv('{}data_frame{}.csv'.format(PR.DIR_PRODUCT_TABLES, page_number), index=False)

        # # export treated rows as csv
        # self.export_treated_rows()

    def build_table(self, ext_pckg=None, ext_series=None):
        # put products in the dictionary
        print("build_table:")

        for area in self.selection_objects:
            print(area)

            if area.type == PFC.TYPE_TITLE:
                for line in area.pdf_line_list:
                    self._series_name = line.find_series_name() if line.find_series_name() else self._series_name
                    for item in line._tabula_line:
                        if 'Panel' in item:
                            self.contains_panel = True
                if not self._series_name:
                    self._series_name = area.pdf_line_list[0]._tabula_line[0]


            elif area.type == PFC.TYPE_CATEG and area.selection_as_line_list[0][0]:
                self.group_prefix = area.selection_as_line_list[0][0] + ' '
                print("group prefix", self.group_prefix)

            elif area.type == PFC.TYPE_COLOR:
                if self.reset_color_areas:
                    # gets True when Stock selection is encountered, the next color area encountered will set all color areas in self.color_areas used property to True and self.reset_color_areas back to False
                    for a in self.color_areas:
                        a.used = True
                    self.reset_color_areas = False

                color_area_obj = area.color_area()
                self.color_areas.append(color_area_obj)

            elif area.type == PFC.TYPE_STOCK:
                self.reset_color_areas = True
                for line in area.pdf_line_list:
                    if line._is_product_table_row:
                        self.description = line.find_subgroup() if line.find_subgroup() else self.description
                        description_splitted = re.split('-', self.description, maxsplit=1)
                        self._subgroup = description_splitted[0].strip()

                        print("self._subgroup", self._subgroup)
                        inline_color = ''
                        (finish, inline_color) = self.find_finish_inline_color(description_splitted)
                        print("finish, inline color", (finish, inline_color))

                        if self.description and (self.group_prefix in self.description):
                            # do not join prefix
                            self.group_prefix = ''

                        g_name = self.group_prefix + line.find_group() if line.find_group() else self.group_prefix.strip()
                        self._group = g_name if g_name else self._group
                        if not self._group and self.contains_panel:
                            self._group = 'Panel'
                        # print("self._group-----------", self._group)
                        # print("contains_panel", self.contains_panel)

                        self._item_size = line.find_item_size() if line.find_item_size() else self._item_size
                        self._units_of_measure = line.find_units_of_measure() if line.find_units_of_measure() else self._units_of_measure
                        self._unit_price = line.find_unit_price() if line.find_unit_price() else self._unit_price

                        # extract packaging data for the item in STOCK area
                        pack_selecions = self.packaging_selections
                        if not pack_selecions:
                            if str(ext_series).lower() == str(self._series_name).lower():
                                pack_selecions = ext_pckg
                        (pc_ctn, sf_ctn, ctn_plt) = self.find_units_per_package(pack_selecions)

                        self._pieces_per_carton = pc_ctn if pc_ctn else self._pieces_per_carton
                        self._sf_per_ctn = sf_ctn if sf_ctn else ""
                        self._ctn_per_plt = ctn_plt if ctn_plt else ""

                        item_code = line.find_vendor_code() if line.find_vendor_code() else self._vendor_code
                        chr = u'\u25CF'
                        count_placeholder = item_code.count(chr)
                        if not count_placeholder:  # chr is not in the item_code
                            self._vendor_code = item_code
                            self._item_color = " ".join((inline_color + " " + finish).split())
                            self.push_attributes()
                        else:
                            left = item_code.split(chr)[0]
                            right = item_code.split(chr)[-1]

                            color_sublist = self.get_color_areas_with_conditions_sublist(self.description)
                            if len(color_sublist):
                                code_color_list = self.get_code_color(color_sublist)
                            else:
                                color_sublist = self.get_color_areas_no_conditions_sublist()
                                code_color_list = self.get_code_color(color_sublist)

                            for (ccode, item_color) in code_color_list:
                                # comment out line below if need to differentiate b/w len of placeholder
                                count_placeholder = len(str(ccode))  # treat all placeholders as having the same len (requirement)
                                if len(str(ccode)) == count_placeholder:
                                    self._vendor_code = str(left) + str(ccode) + str(right)
                                    self._item_color = " ".join((item_color + " " + inline_color + " " + finish).split())
                                    self.push_attributes()

                        # self._item_color = line.find_item_color() if line.find_item_color() else self._item_color
                        #



        # print("Attributes:")
        # print(self._series_name)
        # print(self._group)
        # print(self._subgroup)
        # print(self._item_size)
        # print(self._units_of_measure)
        # print(self._unit_price)
        # print(self._units_per_carton)

        # for item in area.selection_as_dict.keys():
        #     if



        """ sees what fields are detected by the PdfLine and builds product table"""
        # for line in self.lines:  # line comes form fixed column recognition
        #
        #     """not TODO skip lines that are not valid, check if line is guessed list if so than it is valid, """
        #     cur_line_string = self.join_list_items(line._tabula_line)
        #     valid_line = False
        #     # for item in self.guessed_rows_strings:
        #     #     if item in cur_line_string:
        #     #         valid_line = True
        #     if cur_line_string in self.guessed_rows_strings or (
        #             'Units' in cur_line_string and 'Price' in cur_line_string):
        #         valid_line = True
        #
        #     if valid_line:  # line matches the auto guessed row
        #         """collect the fields"""
        #         self._series_name = line.find_series_name() if line.find_series_name() else self._series_name
        #         self._group = line.find_group() if line.find_group() else self._group
        #         self._subgroup = line.find_subgroup() if line.find_subgroup() else self._subgroup
        #         self._vendor_code = line.find_vendor_code() if line.find_vendor_code() else self._vendor_code
        #         self._item_size = line.find_item_size() if line.find_item_size() else self._item_size
        #         self._item_color = line.find_item_color() if line.find_item_color() else self._item_color
        #         self._units_per_carton = line.find_units_per_carton() if line.find_units_per_carton() else self._units_per_carton
        #         self._units_of_measure = line.find_units_of_measure() if line.find_units_of_measure() else self._units_of_measure
        #         self._unit_price = line.find_unit_price() if line.find_unit_price() else self._unit_price
        #
        #         multiplier = 1  # number of times the row must be multiplied
        #         if self.colors:  # if color list is present, a product row will be appended the number of colors times
        #             multiplier = len(self.colors)

        #         if line._is_product_table_row and self._series_name:
        #             # print("is_product_table_row: ", line._is_product_table_row)
        #             # print("_series_name", self._series_name)
        #
        #             """push properties to the dictionary"""
        #             for i in range(multiplier):
        #                 for key in PFC.PRODUCT_TABLE_FIELDS:
        #                     if self.colors and key == "_item_color":
        #                         value = self.colors[i]
        #                     else:
        #                         value = eval("self.%s" % (key))  # line at key
        #                     self.__products[key].append(value)
        #
        #     # print(valid_line, cur_line_string)

    def get_products(self):
        """@:returns the dictionary of products representing product table of the page"""
        return self.__products

    # def export_treated_rows(self):
    #     """ export treated rows as csv"""
    #     frame = []
    #     for line in self.lines:
    #         frame.append(line._row)
    #     with open("{}treated{}.csv".format(PR.DIR_TREATED_ROWS, self._pagenumber), "w", newline='') as f:
    #         wr = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
    #         wr.writerows(frame)

    def join_list_items(self, list_obj):
        line_string_list = [str(item) for item in list_obj]  # strignify any non-string types of items of the list
        line_string = "".join(line_string_list)  # join all items in one string (with no spaces between items)
        line_string = "".join(line_string.split())
        return line_string

    def set_selection_types(self):
        try:
            # initialize selection's type:
            self.selection_objects[0].set_type(PFC.TYPE_TITLE)  # set the first area to title area
            # set remaining areas
            for i in range(1, len(self.selection_objects)):
                self.selection_objects[i].set_type()
        except IndexError:
            print(f"No selections on page {self._pagenumber}")

    def collect_packaging_selections(self):
        """ :return a list of packaging selections of the current page"""
        packaging_selections = []
        for selection in self.selection_objects:
            if selection.type == PFC.TYPE_PACKAGING:
                packaging_selections.append(selection)
        return packaging_selections

    def push_attributes(self, multiplier=1):
        """push properties to the dictionary"""
        for i in range(multiplier):
            for key in PFC.PRODUCT_TABLE_FIELDS:
                if self.colors and key == "_item_color":
                    value = self.colors[i]
                else:
                    value = eval("self.%s" % (key))  # line at key
                self.__products[key].append(value)

    def set_color_multiplier(self, color_areas):
        """ :return color multiplier according to the length of all areas in the list containing color areas
        if no color areas found, return 1 """
        m = 0
        for area in color_areas:
            m += area.length
        return m if m > 0 else 1

    def get_code_color(self, color_areas):
        """ :return a list of tuples (color_code, item_color)
        for all areas where area.used == False"""
        code_color = []
        for area in color_areas:
            if not area.used:
                for i in range(area.length):
                    color_code = area.color_dict.get('Code')[i]
                    item_color = []
                    for key in area.color_dict.keys():
                        item_color.append(str(area.color_dict[key][i]))
                    item_color = " ".join(item_color)
                    code_color.append((color_code, item_color))
        return code_color

    def get_color_conditions(self):
        conditions = []
        for area in self.color_areas:
            if not area.used:
                conditions.append(area.condition)
        return conditions

    def get_color_areas_with_conditions_sublist(self, description):
        color_sublist = []
        for a in self.color_areas:
            if a.condition and a.condition in description:
                color_sublist.append(a)
        return color_sublist

    def get_color_areas_no_conditions_sublist(self):
        color_sublist = []
        for a in self.color_areas:
            if not a.condition:
                color_sublist.append(a)
        return color_sublist

    def find_units_per_package(self, packaging_selections):
        """:return a tuple (pieces_per_carton, sf_per_carton, carton_per_pallet) for the product in the current line """
        pc_ctn = None  # pieces per carton
        sf_ctn = None
        ctn_plt = None
        upp_options = [] # units per package options

        for selection in packaging_selections:
            index_of_pc_per_ctn = None
            index_of_sf_per_ctn = None
            index_of_ctn_per_plt = None
            for packaging_line in selection.pdf_line_list:
                if 'Pcs/Ctn' in packaging_line._tabula_line:
                    index_of_pc_per_ctn = packaging_line._tabula_line.index('Pcs/Ctn')
                if 'Sf/Ctn' in packaging_line._tabula_line:
                    index_of_sf_per_ctn = packaging_line._tabula_line.index('Sf/Ctn')
                if 'Ctn/Plt' in packaging_line._tabula_line:
                    index_of_ctn_per_plt = packaging_line._tabula_line.index('Ctn/Plt')
                indexes = (index_of_pc_per_ctn, index_of_sf_per_ctn, index_of_ctn_per_plt)
                label_pcctn_sfctn_ctnplt = packaging_line.labeled_units_per_package(self.description, self._item_size,
                                                                                    indexes)
                upp_options.append(label_pcctn_sfctn_ctnplt)
        if upp_options:
            upp_options.reverse() # in case old and new info is presented, will grab the last one
            upp_options.sort(reverse=True, key=lambda item: item[0])

            # print("upp_options", upp_options)

            pc_ctn = upp_options[0][1]  # units per carton is the 2nd item of the first tuple of the sorted tuple list
            sf_ctn = upp_options[0][2]
            ctn_plt = upp_options[0][3]
        return (pc_ctn, sf_ctn, ctn_plt)



    def config_row_number(self, itemname):
        """ @:returns row number of TARGET_CONFIG.csv
            @:param itemname is the name to look for in th names column of the TARGET_CONFIG.csv"""
        # print("itemname", itemname)
        row_n = None
        missing_name = ""
        for i in range(len(self._config["NAMES"])):
            name_list = self._config["NAMES"][i].split(sep=',')
            for name in name_list:
                if name in itemname.upper():
                    row_n = i
                missing_name = name
        # print("missing_name", missing_name)
        return row_n

    def find_finish_inline_color(self, description_splitted):
        finish = ''
        inline_color = ''
        if len(description_splitted) == 2:
            description_splitted = description_splitted[-1].split('-', maxsplit=1)
            if len(description_splitted) == 2:
                inline_color = description_splitted[0]
                finish = description_splitted[-1]
            else:
                finish = description_splitted[-1]
        return (finish, inline_color)



