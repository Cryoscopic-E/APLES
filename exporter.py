import copy
import datetime
from openpyxl import load_workbook
import pandas as pd
from openpyxl.styles import numbers, Alignment

exported = './data/exported1.xlsx'
sheet = './data/sheet1.csv'
sheet2 = './data/sheet2.csv'
def export_to_excel():
    df = pd.read_csv(sheet)
    writer = pd.ExcelWriter(exported, engine='openpyxl', mode='a', if_sheet_exists='replace')
    df.to_excel(writer, sheet_name='tasks', index=None)
    writer.close()
    
    df = pd.read_csv(sheet2)

    with pd.ExcelWriter(exported, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name='challenges', index=False)
        workbook = writer.book
        s = workbook['tasks']
        
        for cell in s[1]:
            cell.style = 'Normal'

    with pd.ExcelWriter(exported, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name='challenges', index=False)

        workbook = writer.book
        s = workbook['challenges']
        
        for cell in s[1]:
            cell.style = 'Normal'

        first_h = True
        for cell in s["H"]:
            if first_h == False:
                cell.value = datetime.datetime.strptime('2024-07-01 6:00', '%Y-%m-%d %H:%M')
                cell.number_format = 'yyyy-mm-dd hh:mm'
            first_h = False
        
        first_g = True
        for cell in s["G"]:
            if first_g == False:
                cell.value = '122'
                cell.number_format = numbers.FORMAT_TEXT
            first_g = False   

        first_s = True
        for cell in s["I"]:
            if first_s == False:
                cell.value = datetime.datetime.strptime('2024-10-01 6:00', '%Y-%m-%d %H:%M')
                cell.number_format = 'yyyy-mm-dd hh:mm'
            first_s = False

        



