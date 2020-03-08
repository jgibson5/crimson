import xlrd

def read_workbook(workbook, item_map):
    wb = xlrd.open_workbook(workbook)

    ignored_sheets = ('itemlist', 'Rules', 'Export Summary')

    default_item_id = item_map['empty']

    user_lists = {}

    for sheet_name in wb.sheet_names():
        if sheet_name in ignored_sheets:
            continue
        sh = wb.sheet_by_name(sheet_name)

        user_lists[sheet_name] = []

        for row in sh.get_rows():
            item_name = row[1].value
            if item_name == 'N U L L' or item_name == '':
                item_name = 'empty'
            user_lists[sheet_name].append(item_map[item_name])

    return user_lists



