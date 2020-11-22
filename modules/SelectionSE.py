from modules.Selection import Selection
from modules.func import config_row_number
from modules.PdfLineSE import PdfLineSE


class SelectionSE(Selection):
    """ Represents area of selection on the page of SEQUEL ENCORE """
    def __init__(self, df, is_se, conf_d):
        super().__init__(df, is_se)
        self._config = conf_d
        # page is from Sequel encore catalog
        self.pdf_line_list = [PdfLineSE(line, conf_d) for line in self.selection_as_line_list]

    def is_color_area(self):
        """ :return true if this is a color area """
        is_color_area = False
        s = self.selection_as_line_list[0]
        # print("self.selection_as_line_list[0]", self.selection_as_line_list[0])

        if len(s) == 1:
            is_color_area = True

        if config_row_number(s[0].split('-')[0], self._config):
            is_color_area = False

        return is_color_area

    def is_categ_area(self):
        """ :return True if this is a category(group area)"""
        is_cat = False
        s = self.selection_as_line_list[0]
        if len(s) == 1:
            if config_row_number(s[0].split('-')[0], self._config):
                is_cat = True
        return is_cat


