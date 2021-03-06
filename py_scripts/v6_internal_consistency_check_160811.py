
# coding: utf-8

# In[ ]:

#! /usr/bin/python3
# Cross-checking MainTable, GISInfoTable from v6 .mdb for internal consistency
# ..checking to see if for each row in MainTable, the unique PT_ID or BOU_ID exists as SYS_ID in GISINfoTable

# NOTE that this was a quick-and-dirty script -- it has NOT been refactored, and was not written with elegance or efficiency in mind.
# It is preserved here merely for record-keeping purposes.  It does NOT need to be re-run as part of a workflow.

from pandas import Series, DataFrame, ExcelWriter
import pandas as pd


# In[ ]:

def write_to_excel(df, filename):
    '''function for creating Excel .xlsx files'''
    writer = ExcelWriter(filename, engine='xlsxwriter')
    df.to_excel(writer)
    writer.save()


# In[ ]:

# import constituent sheets from Excel spreadsheet as DataFrames, and then concatenate them together (Excel sheets are size-limited to ~64k entries)
GISInfo_one = pd.read_excel('/home/sf/Dropbox/1608_CHGIS/GISInfoTable.xls', sheetname='GISInfoTable')
GISInfo_two = pd.read_excel('/home/sf/Dropbox/1608_CHGIS/GISInfoTable.xls', sheetname='part2')
GISInfo = pd.concat([GISInfo_one, GISInfo_two], axis=0)
Main_one = pd.read_excel('/home/sf/Dropbox/1608_CHGIS/MainTable.xls', sheetname='MainTable')
Main_two = pd.read_excel('/home/sf/Dropbox/1608_CHGIS/MainTable.xls', sheetname='part2')
Main_three = pd.read_excel('/home/sf/Dropbox/1608_CHGIS/MainTable.xls', sheetname='part3')
Main = pd.concat([Main_one, Main_two, Main_three], axis=0)


# In[ ]:

# add cols to MainTable, indicating which rows have BOU_ID or PT_ID that match a GISInfoTable row's SYS_ID
Main['BOU_ID_IN_GISINFO_SYS_ID'] = Main['BOU_ID'].isin(GISInfo['SYS_ID'])
Main['PT_ID_IN_GISINFO_SYS_ID'] = Main['PT_ID'].isin(GISInfo['SYS_ID'])

# add flags to MainTable, for 1) rows that match nothing in GISInfo, 2) rows that match something in GISInfo twice
Main['ISSUE?'] = (Main['BOU_ID_IN_GISINFO_SYS_ID'] == Main['PT_ID_IN_GISINFO_SYS_ID'])
Main['BOU_ID_EQUALS_PT_ID'] = (Main['BOU_ID'] == Main['PT_ID'])


# In[ ]:

# output MainTable to new .xlsx file
write_to_excel(Main, 'MainTable_mod.xlsx')


# In[ ]:

# cols to GISInfoTable, indicating which rows have SYS_ID that match a MainTable row's BOU_ID or PT_ID
GISInfo['SYS_ID_IN_MAIN_BOU_ID'] = GISInfo['SYS_ID'].isin(Main['BOU_ID']) 
GISInfo['SYS_ID_IN_MAIN_PT_ID'] = GISInfo['SYS_ID'].isin(Main['PT_ID'])


# In[ ]:

# output GISInfoTable to new .xlsx file
write_to_excel(GISInfo, 'GISInfoTable_mod.xlsx')


# In[ ]:

# check for duplicates within GISInfoTable; duplicates already accounted for in MainTable_mod.xlsx
# GISInfo_test = GISInfo.duplicated(subset=['SYS_ID'], keep=False)    
# print(GISInfo_test.sort_values(ascending=False))

