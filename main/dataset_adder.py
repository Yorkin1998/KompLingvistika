import os
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

import openpyxl
from main.models import OT, SIFAT

path = "/home/yorkin1998/Desktop/STUDY/MorphApp/main/dataset.xlsx"

wb_obj = openpyxl.load_workbook(path,data_only=True)
sheet_obj = wb_obj.active

print("Boshlandi")
for i in range(1,1000):
    if sheet_obj.cell(row=i, column=1).value:
        OT.objects.create(
            word = sheet_obj.cell(row=i, column=1).value
        )
    if sheet_obj.cell(row=i, column=2).value:
        SIFAT.objects.create(
            word = sheet_obj.cell(row=i, column=2).value
        )
print("Tugadi")