import csv

csv_file = file('names.csv', 'w')

writer = csv.writer(csv_file)
writer.writerow(['Store1'])

field_names = ['first_name', 'last_name']
dict_writer = csv.DictWriter(csv_file, fieldnames=field_names)

for i in range(436):
	print i

	writer.writerow(['Store2'])
	dict_writer.writeheader()
	dict_writer.writerow({'first_name': '1', 'last_name': 'Beans'})
	dict_writer.writerow({'first_name': 'Lovely', 'last_name': 'Spam'})
	dict_writer.writerow({'first_name': 'Wonderful', 'last_name': 'Spam'})

	writer.writerow([' '])
	writer.writerow([' '])