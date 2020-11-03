""" contains pdf constants to detect attributes """

ITEM_ROW_LEN = {5, 6, 7}  # number of possible columns in an itemrow
EMPTY_LINE_FLAGS = {"Carton"}
DETECT_SERIES_SET = {"Units/", "U/M", "Price"}
VENDOR_CODE_INDEX = 1  # index of the item of the list that contains vendor code

# EXTERNAL DATA
VENDOR_NAME_CODE = "V006"
vendor1_name = "V006 DALTILE"
vendor1_subsidiary = 3
vendor2_subsidiary = 4

PRODUCT_TABLE_FIELDS = [
    "_pagenumber",
    "_series_name",
    "_group",
    "_item_size",
    "_vendor_code",
    "_subgroup",
    "_item_color",
    "_units_per_carton",
    "_units_of_measure",
    "_unit_price"
]


TYPE_TITLE = 'TITLE_AREA'
TYPE_CATEG = 'CATEG_AREA'
TYPE_COLOR = 'COLOR_AREA'
TYPE_STOCK = 'STOCK_AREA'
TYPE_PACKAGING = 'PACKAGING_AREA'



COLUMN_X_COORDINATES = [120.024,219.621,339.538, 465.504, 505.089, 532.494, 573.602]  # x coordinates of columns for tabula.read_pdf

TABLE_COORDINATES = (31.591, 17.128, 740.303, 591.110) #Portion of the page to analyze(top,left,bottom,right) $y1,$x1,$y2,$x2

END_OF_TABLE_FLAGS = [
    "See below or next page"
]