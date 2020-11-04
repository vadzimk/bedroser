import modules.PDF_CONST as PFC
from modules.func import *

class PdfLine:
    """A line of the Pdf input file"""

    @staticmethod
    def token_is_blank(csv_list_item):
        return csv_list_item == '\"\"' or not csv_list_item or "Unnamed:" in str(
            csv_list_item) or csv_list_item == '\xf8'

    def __init__(self, tabula_csv_reader_list_line):
        """ @:param page_data_set for better detection of tokens"""
        # self._page_data_set = page_data_set
        self._tabula_line = tabula_csv_reader_list_line

        # self._row = self.treat_row()  # check for matches with page_data_set

        self._line_len = len(self._tabula_line)  # number of items in the list representing the row
        self._num_blanks = self.count_blanks()
        # self._all_cells_filled = self.all_cells_filled()  # applies to a table row only
        # self._is_color_table_header = self.is_color_table_header()
        # self._is_color_table_row = self.is_color_table_row()
        self._is_product_table_row = self.is_product_table_row()

        print(self._line_len, self._num_blanks, self._tabula_line)

        # print(len(self._row), self._row)

    # def contains_series(self):
    #     """ detects series name in the row"""
    #     return PFC.DETECT_SERIES_SET.issubset(set(self._tabula_line))

    def find_series_name(self):
        """ :returns series name or None if not found """
        name = None
        if len(self._tabula_line) == 1:
            for item in self._tabula_line:
                if 'CATEGORY' in str(item):
                    the_list = item.split('-')
                    name = the_list[-1]
                    name = " ".join(name.split())  # remove multiple spaces

        return name

    def count_blanks(self):
        """ counts number of blanks in a given row"""
        count = 0
        for token in self._tabula_line:
            if PdfLine.token_is_blank(token):
                count += 1
        return count

    # def contains_group(self):
    #     """ :returns true if row contains group name, false otherwise"""
    #     contains = False
    #     # if not self._tabula_line[-1] and not self._tabula_line[-2] and not self._tabula_line[-3]:
    #     #     contains = True
    #     # # print("contains group: ", self._tablula_line[-3:], contains, self._tablula_line)
    #     return contains

    def find_group(self):

        group_name = None
        index = 0
        if self._is_product_table_row:
            group_name = self._tabula_line[index]
            if self._line_len == 5:  # the prefix above the line became the column header
                group_name = " ".join(group_name.split()[:-1]) if len(group_name.split()) > 1 else None
            elif self._line_len == 7:
                group_name = " ".join(self._tabula_line[:2]).replace('\xf8', '').strip()
        if 'Stock' in group_name or 'NEW' in group_name or 'Only' in group_name or 'Discontinued' in group_name:
            group_name = None

        return group_name

    # def contains_subgroup(self):
    #     return self._is_product_table_row

    # def subgoup_index(self):
    #     return 2

    def find_subgroup(self):
        subgroup_name = None
        index = -3
        if self._is_product_table_row:
            if self._line_len == 6 or self._line_len == 7 or (self._line_len == 5 and self._num_blanks == 0):
                subgroup_name = self._tabula_line[index]
            elif self._line_len == 5 and self._num_blanks == 1:  # the prefix above the line became the column header
                index = -4
                subgroup_name = self._tabula_line[index]
                subgroup_name = " ".join(subgroup_name.split()[1:])
        return subgroup_name.replace('*', '')

    def find_group_prefix(self):
        """ :return subcategory or empty string """
        subcat = ''
        index = 0
        if self.is_group_prefix_row():
            subcat = self._tabula_line[0]
        return subcat

    # def contains_item_size(self):
    #     return self._is_product_table_row
    #     # return self.all_cells_filled()

    def find_item_size(self):
        item_size = None
        index = -4
        if self._is_product_table_row:
            item_size = self._tabula_line[index]
            if self._line_len == 5 and self._num_blanks == 1:
                item_size = item_size.split()[0]
        return item_size

    # def contains_vendor_code(self):
    #     return self._is_product_table_row

    # def vendor_code_index(self):
    #     return 1

    def find_vendor_code(self):

        code = None
        if self._tabula_line[-5]:
            index = -5
        else:
            index = -6

        if self._is_product_table_row:
            code = self._tabula_line[index]
            if len(self._tabula_line) == 5:
                code = code.split()[-1]
            code = code.replace('\xf8', '').strip()
        return code

    # def contains_color(self):
    #     contains = False
    #     if self._is_product_table_row:
    #         if self._tabula_line[3]:
    #             contains = True
    #     return contains

    # def color_index(self):
    #     return 3

    def find_item_color(self):
        color = None
        # if self.contains_color() and self._is_product_table_row:
        #     index = 3
        #     color = str(self._tabula_line[index])
        #     color = " ".join(color.split())
        # # elif self.contains_color() and self._is_color_table_row:
        # #     color = ' '.join(self._row).strip()
        return color

    # def contains_units_per_carton(self):
    #     pass

    def find_units_per_carton(self, description, size):

        # print(description)
        # print(size)
        # print(self._tabula_line)

        description_arr = description.split()
        size_arr = size.split()

        # if description == 'Deco Liner - Matte':
        #     print("find_units_per_carton: ")
        #     print("description:", description_arr)
        #     print("size:", size_arr)
        #     print(self._tabula_line)

        upc = None
        label = 0
        index = 1
        if "Pcs/Ctn" not in self._tabula_line:
            packaging_info_set = set(str(self._tabula_line[0]).split())

            for p_item in packaging_info_set:
                for d_item in description_arr:
                    if d_item == p_item:
                        label += 1
                    # print(d_item , p_item, d_item == p_item)

                for s_item in size_arr:
                    if s_item == p_item or dim_equals(fract_dim_to_float_dim(s_item), p_item):
                        label += 1
                    # print(s_item, p_item, s_item == p_item, dim_equals(fract_dim_to_float_dim(s_item), p_item))

            if label > 0:
                upc = self._tabula_line[index]
        # print(label, upc)
        return (label, upc)



    def find_units_of_measure(self):
        uom = None
        index = -2
        if self._is_product_table_row:
            uom = self._tabula_line[-2]
        return uom

    def find_unit_price(self):
        up = None
        index = -1
        if self._is_product_table_row:
            up = self._tabula_line[index]
        return up

    def is_product_table_row(self):
        """returns true if the row contains price information  - the longest row of the stock selection """
        row_set = set(self._tabula_line)
        is_valid = False
        if self._line_len >= 5 and self._tabula_line[-1] and not 'Net Price' in str(self._tabula_line[-1]):
            is_valid = True
        return is_valid

    def is_group_prefix_row(self):
        is_gr_prefx = False
        if self._line_len == 5 and self._num_blanks >= 3:
            is_gr_prefx = True
        return is_gr_prefx

    # def is_color_table_header(self):
    #     is_header = False
    #     if 'Code' in self._tabula_line:
    #         if 'Name' in self._tabula_line:
    #             is_header = True
    #         else:
    #             for item in self._tabula_line:
    #                 if "Color" in str(item):
    #                     is_header = True
    #     return is_header
    #
    # def is_color_table_row(self):
    #     return False

    # def extract_first_match(self, phrase):
    #     """ @:param phrase is a string with spaces that needs to be broken in several tokens that are present in page_data_set
    #     @:returns recursively smaller phrase that is either empty string or contained in the page_data_set """
    #     if len(phrase) == 0:
    #         return phrase
    #     elif phrase in self._page_data_set:
    #         return phrase
    #     else:
    #         return self.extract_first_match(" ".join(phrase.split()[:-1]))  # remove the last word from the token
    #
    # def treat_row(self):
    #     """ compares token in row to the html dataset and separates string into items that are present in the html dataset"""
    #     tabula_line = []
    #     for token in self._tablula_line:
    #         tabula_line.append(" ".join(str(token).split()))
    #
    #     row = []
    #     for phrase in tabula_line:
    #         if phrase == "":
    #             row.append(phrase)
    #         else:
    #             i = 0  # holds index of the next place to search for a token
    #             while i < len(phrase):
    #                 le = len(phrase[i:])
    #                 fixed = self.extract_first_match(phrase[i:])
    #
    #                 if not fixed == '':
    #                     row.append(fixed)
    #                 i = phrase.index(fixed) + len(fixed) + 1  # points to the beginning of next token in phrase
    #                 if i < le:
    #                     phrase = phrase[i:]  # make next token first
    #                 else:
    #                     break
    #                 i = 0
    #
    #     return row
