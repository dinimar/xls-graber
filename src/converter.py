import csv
import os
from openpyxl import Workbook
from openpyxl import load_workbook

root = "c:/Users/Dinir/Documents/git/nativeskatestore-graber/"
q_file = "resources/20-questions-upd.csv"
out = "resources/out/upd-questions.xlsx"

fieldnames = {'Id': 1, 'Type': 2, 'ParentIdInFile': 3, 'ParentIdInSIte': 4, 
				'Title': 5, 'Content': 6, 'Format': 7, 'CategoryId': 8, 'CategoryUrl': 9,
				'Tags': 10, 'UserName': 11, 'AnonymousName': 12, 'Notify': 13, 'ExtraValue': 14, 
				'DateTimeFrom': 15, 'DateTimeTo': 16, 'Selected': 17}

last_free_row = 1

if os.path.isfile(out):
	wb_q = load_workbook(filename=os.path.join(root, out))
else:
    wb_q = Workbook()

with open(os.path.join(root, q_file), newline='', encoding='utf-8') as csvfile:
	# reader = csv.DictReader(csvfile)
	spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
	wb_q_s = wb_q.active
	for row in spamreader:
	    wb_q_s.cell(column=fieldnames['Id'], row=last_free_row).value = row[fieldnames['Id']-1]
	    wb_q_s.cell(column=fieldnames['Type'], row=last_free_row).value = row[fieldnames['Type']-1]
	    wb_q_s.cell(column=fieldnames['ParentIdInFile'], row=last_free_row).value = row[fieldnames['ParentIdInFile']-1]
	    wb_q_s.cell(column=fieldnames['ParentIdInSIte'], row=last_free_row).value = row[fieldnames['ParentIdInSIte']-1]
	    wb_q_s.cell(column=fieldnames['Title'], row=last_free_row).value = row[fieldnames['Title']-1]
	    wb_q_s.cell(column=fieldnames['Content'], row=last_free_row).value = row[fieldnames['Content']-1]
	    wb_q_s.cell(column=fieldnames['Format'], row=last_free_row).value = row[fieldnames['Format']-1]
	    wb_q_s.cell(column=fieldnames['CategoryId'], row=last_free_row).value = row[fieldnames['CategoryId']-1]
	    wb_q_s.cell(column=fieldnames['CategoryUrl'], row=last_free_row).value = row[fieldnames['CategoryUrl']-1]
	    wb_q_s.cell(column=fieldnames['Tags'], row=last_free_row).value = row[fieldnames['Tags']-1]
	    wb_q_s.cell(column=fieldnames['UserName'], row=last_free_row).value = row[fieldnames['UserName']-1]
	    wb_q_s.cell(column=fieldnames['AnonymousName'], row=last_free_row).value = row[fieldnames['AnonymousName']-1]
	    wb_q_s.cell(column=fieldnames['Notify'], row=last_free_row).value = row[fieldnames['Notify']-1]
	    wb_q_s.cell(column=fieldnames['ExtraValue'], row=last_free_row).value = row[fieldnames['ExtraValue']-1]
	    wb_q_s.cell(column=fieldnames['DateTimeFrom'], row=last_free_row).value = row[fieldnames['DateTimeFrom']-1]
	    wb_q_s.cell(column=fieldnames['DateTimeTo'], row=last_free_row).value = row[fieldnames['DateTimeTo']-1]
	    wb_q_s.cell(column=fieldnames['Selected'], row=last_free_row).value = row[fieldnames['Selected']-1]
	    last_free_row = last_free_row + 1

wb_q.save(filename=os.path.join(root, out))

