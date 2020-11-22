from modules.func import *
import sys
import time
from modules.PdfDoc import PdfDoc
from modules.tf import create_target_and_uom

list_of_pages_with_doubled_rows = None


def main():
    DOC_SELECTIONS_COORDINATES = find_tabula_template_json_filename()

    try:
        cleanup()
        create_project()
    except PermissionError:
        print(f"Access to the project folder denied\nClose applications that might use it and try again")
        input(f"Press any key to close the window")
        return

    args = sys.argv  # get the list of arguments
    infilename = None
    if len(args) == 2:
        infilename = 'Bedros.pdf'
        if not os.path.exists(infilename) or not os.path.isfile(infilename):
            print(f"Default input file not found")
            infilename = None
    if not infilename:
        infilename = ask_for_filename(args)

    print(f"Chosen file: {infilename}")

    infilename_n_pages = determine_n_pages(infilename)
    print(f"The number of pages in this file is: {infilename_n_pages}")


    page_start = ask_for_starting_page(infilename_n_pages)
    print(f"Chosen starting page: {page_start}")


    n_pages_to_process = ask_for_n_pages(infilename_n_pages, page_start)
    if n_pages_to_process == "ALL":
        n_pages_to_process = infilename_n_pages - page_start + 1
    else:
        n_pages_to_process = n_pages_to_process or 1

    print(f"Chosen number of pages to process: {n_pages_to_process}")

    se_page_range = (None, None)

    has_se = input("Is SEQUEL ENCORE in this page range? (y/n): ")

    while not (has_se.lower() == 'y' or has_se.lower() == 'n'):
        print(f"Invalid answer")
        has_se = input("Is SEQUEL ENCORE in this page range? (y/n): ")

    list_of_pages_with_doubled_rows = []
    if has_se.lower() == 'y':
        se_page_range = ask_for_se_range(page_start, n_pages_to_process)
        list_of_pages_with_doubled_rows = ask_for_pages_with_doubled_rows(
            page_start, page_start + n_pages_to_process - 1)

    selection_dfs_cache = 'cache.pickle'

    # ============= option to use cache ============
    rescan = None
    if os.path.exists(selection_dfs_cache):
        print(f"Found {selection_dfs_cache}")
        rescan = input(f"Rescan pages? (y/n): ")
        if rescan.lower()=='y':
            rescan = True
        else:
            rescan = False
    # ==============================================

    print(f"Working on {infilename}\nPlease wait....")
    start_time = time.time()

    config_dictionary = read_to_dict(PR.TARGET_CONFIG)

    pickled_d = {}
    if not rescan:
        pickled_d = import_selection_dataframes(selection_dfs_cache)

    price_list = PdfDoc(in_file_name=infilename,
                        pickled_data=pickled_d,
                        template_json=DOC_SELECTIONS_COORDINATES,
                        config_dict=config_dictionary,
                        se_range=se_page_range,
                        doubled_rows_pagens=list_of_pages_with_doubled_rows,
                        page_start=page_start,
                        n_pages=n_pages_to_process,
                        )

    print(f"Reading pages:")
    price_list.create_pages()

    # # ================== for debugging
    # dfs = price_list.collect_selection_dfs()
    # export_selection_dataframes(dfs, selection_dfs_cache)  # in file
    #
    # # ======================

    print(f"For each page: creating product tables...")
    price_list.create_product_tables()

    print(f"Aggregating data from all tables...")
    price_list.construct_cumulative_dict()

    print(f"Exporting into the file {PR.DOC_PRODUCT_TABLE}")
    try:
        price_list.export_cumulative_dict(PR.DOC_PRODUCT_TABLE)
    except PermissionError:
        print(f"Access to {PR.DOC_PRODUCT_TABLE} denied\nClose applications that might use it and try again")
        input(f"Press any key to close the window")
        return

    end_time = time.time()
    hours, rem = divmod(end_time - start_time, 3600)
    minutes, seconds = divmod(rem, 60)
    print(f"Task finished.\n"
          f"Time elapsed: {minutes:.0f} min {seconds:.0f} sec\n"
          f"See:\n{PR.DIR_PROJECT}product_table.csv\n")

    create_target_uom_files = input(f"Create target.csv, uom.csv (y/n) ? ")

    print(f"Creating template file and UOM file...")
    if create_target_uom_files.lower() == 'y':
        try:
            create_target_and_uom()
        except PermissionError:
            print(
                f"Access to {PR.DOC_UOM} or {PR.DOC_TARGET} denied\nClose applications that might use it and try again")
            input(f"Press any key to close the window")
            return

    print(f"Task finished.\n"
          f"{PR.DOC_TARGET}\n"
          f"{PR.DOC_UOM}")


if __name__ == "__main__":
    main()
