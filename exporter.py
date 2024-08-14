from openpyxl import load_workbook
import pandas as pd

exported = './data/exported1.xlsx'
sheet = './data/sheet1.csv'
sheet2 = './data/sheet2.csv'
def export_to_excel():
    df = pd.read_csv(sheet)
    writer = pd.ExcelWriter(exported, engine='openpyxl', mode='a', if_sheet_exists='replace')
    df.to_excel(writer, sheet_name='tasks', index=None)
    writer.close()
    
    df = pd.read_csv(sheet2)
    writer = pd.ExcelWriter(exported, engine='openpyxl', mode='a', if_sheet_exists='replace')

    df.to_excel(writer, sheet_name='challenges', index=None)
    writer.close()

