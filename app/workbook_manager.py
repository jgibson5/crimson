import xlrd
import xlwt

def read_workbook(workbook, item_map):
    wb = xlrd.open_workbook(workbook)

    ignored_sheets = ('itemlist', 'Rules', 'Export Summary', 'Completed')

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

def write_workbook(user_lists, all_items, path):
    wb = xlwt.Workbook()
    item_list_sheet = wb.add_sheet('itemlist')

    i = 1
    for item in all_items:
        item_list_sheet.write(i, 1, item)
        i += 1

    for user in user_lists.keys():
        user_list = user_lists[user]

        user_list_sheet = wb.add_sheet(user)
        i = 1
        for item in user_list:
            user_list_sheet.write(i, 1, f"Item {i}")
            user_list_sheet.write(i, 2, item)
            i += 1

    wb.save(path)
