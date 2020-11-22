import re

from modules.PdfLine import PdfLine
from modules.func import config_row_number


class PdfLineSE(PdfLine):
    def __init__(self, tabula_csv_reader_list_line, conf_d):
        super().__init__(tabula_csv_reader_list_line)
        # test_d = {'NAMES':['GRANITE SLAB, MARBLE SLAB, QUARTZITE SLAB, SCHIST SLAB, SLAB, PREFAB']}
        self.conf_d = conf_d


    def find_group(self):
        group_name = None
        index = 0
        row_n = None

        done = False
        for item in self._tabula_line:

            for i in range(len(self.conf_d["NAMES"])):
                name_list = self.conf_d["NAMES"][i].split(sep=',')
                name_list = [name.strip() for name in name_list]  # trim whitespace

                for name in name_list:
                    if name in str(item).upper():
                        # print("find_group", name, str(item).upper())
                        group_name = name
                        # start = item.upper().index(name.upper())
                        # group_name = re.split(r'\W', item[start:].upper())[0]
                        # print("inside group_name", group_name)
                        done = True
                        break

                if done:
                    break
            if done:
                break

        # print("group_name", group_name)

        return group_name


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
            if len(self._tabula_line) == 7: # there is Category column
                # append category
                code = self._tabula_line[1] + ' ' + code
            code = code.replace('\xf8', '').strip()
        return code
