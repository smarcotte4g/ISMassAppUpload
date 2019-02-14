import xlrd
import csv
import os

def csv_from_excel(filename):

    wb = xlrd.open_workbook(f'files/{filename}', on_demand=True)
    shnum = wb.sheet_names()
    for x in shnum:
        base, _ = os.path.splitext(filename)
        sh = wb.sheet_by_name(x)
        your_csv_file = open(f'output/{base}_{x}.csv', 'w', newline='', encoding='utf-8')
        wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)
        for rownum in range(sh.nrows):
            wr.writerow(sh.row_values(rownum))
        your_csv_file.close()

if __name__ == "__main__":
    directory = os.fsencode('/files') # Might need full path to files
    os.makedirs('/output', exist_ok=True) # Probably need full path here to output
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            csv_from_excel(filename)