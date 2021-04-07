from ftplib import FTP
import datetime
from conf.settings.base import MEDIA_ROOT
import os
from django.core.files.storage import default_storage
import csv
from os import listdir
from os.path import isfile, join
import io
from parts.models import Part

csv_folder = os.path.join(MEDIA_ROOT, 'import-csv')


def set_filename():
    now = datetime.datetime.now()
    time_stamp = now.strftime("%d-%m-%Y_%H:%M")  # %d-%m-%Y-%H:%M
    return f'parts-{time_stamp}.csv'


def handle_uploaded_csv_file(f):
    # with open(f"{os.path.join(MEDIA_ROOT, 'upload-csv')}/file.csv", 'wb+') as destination:
    local_filename = set_filename()
    with open(os.path.join(csv_folder, local_filename), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return local_filename

def get_data_from_csv(filename, delimiter=';'):
    data = []
    f = default_storage.open(os.path.join(csv_folder, filename), 'r')
    reader = csv.reader(f, delimiter=delimiter)
    # next(reader)
    for row in reader:
        data.append(row)
    f.close()

    return data

def take_files_form_csv_folder():
    myfiles = [f for f in listdir(csv_folder) if isfile(join(csv_folder, f))]
    return myfiles

def file_remove(filename):
    path = os.path.join(csv_folder, filename)
    try:
        os.remove(path)
        return {'status': 1, 'text': f'Файл {filename} успешно удален'}
    except OSError as error:
        return {'status': 0, 'text': error}

# def import_parts(filename):
#     '''
#     Create part instances from local csv file
#     '''
#     count = 0
#     data = get_data_from_csv(filename)
#     for row in data:
#         if row[0] and row[1] and row[2]:
#             count += 1
#             _, created = Part.objects.get_or_create(
#                 vin=row[0],
#                 code=row[1],
#                 name=row[2],
#                 # unit = row[3],
#                 # count = row[4],
#                 )
#     return count
