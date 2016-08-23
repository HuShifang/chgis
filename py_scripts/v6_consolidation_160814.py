
# coding: utf-8

# In[1]:

#! /usr/bin/python3

# /v6_consolidation_160814.ipynb
# /py_scripts/v6_consolidation_160814.py

# A script for consolidating .csv files extracted from a Microsoft Access (.mdb) file containing CHGIS v6 data provided by Fudan University 复旦大学 
# There are two .csv files being consolidated: one contains the full contents of the original .mdb file's GISInfoTable, and the other contains only those elements in the .mdb file's MainTable that did not exist in GISInfoTable.
# These files ultimately trace back to the quick-and-dirty script work in /v6_internal_consistency_check_160811.ipynb and the .py script of the same name, but additional manipulation had been done on that script's output using LibreOffice
# This script's output forms half of the basis for version_merge_160822.ipynb 

import pandas as pd
import numpy as np
from pandas import DataFrame, Series


# In[2]:

# import .csv files as dataframes 
v6_GISInfo = pd.read_csv('input/v6_GISInfoTable_2016-08-09.csv', low_memory=False)
v6_Main_only = pd.read_csv('input/MainTable_and_not_GISInfoTable.csv', low_memory=False)


# In[3]:

def progress_check(df, name):
    '''function for exporting dataframes to .csv files, for progress-checking'''
    df.to_csv('TESTING_%s.csv' % name)


# In[22]:

# append all the rows that had IDs in MainTable that aren't in the original GISInfoTable
# Rule: where bou_id and pt_id are the same, if x&y are empty or =0s, use bou_id and set type to POLYGON
#           ...if x&y !=0, use PT_ID and set as POINT object types

# generating DataFrame of "normal" ('BOU_ID'==0), point items from MainTableOnly
mask_normal = v6_Main_only['BOU_ID'] == 0
Main_normal = v6_Main_only[mask_normal]
Main_normal['orig_id'] = Main_normal['PT_ID']
Main_normal['obj_type'] = 'POINT'

# preparing DataFrame of "abnormal" ('BOU_ID' == 'PT_ID') rows from MainTableOnly
mask_abnormal = v6_Main_only['BOU_ID'] == v6_Main_only['PT_ID']
Main_abnormal = v6_Main_only[mask_abnormal]

# generating DataFrame of polygon rows from abnormal rows from MainTableOnly
http://localhost:8888/notebooks/mask_polygons = Main_abnormal['X_COOR'] == 0
Main_abnormal_polygons = Main_abnormal[mask_polygons]
Main_abnormal_polygons['orig_id'] = Main_abnormal_polygons['BOU_ID']
Main_abnormal_polygons['obj_type'] = 'POLYGON'

# generating DataFrame of point rows from abnormal rows from MainTableOnly
# TODO: SEE IF THIS CAN BE DRY-ED OUT AND COMBINED WITH THE ABOVE Main_normal STUFF
mask_points = Main_abnormal['X_COOR'] != 0
Main_abnormal_points = Main_abnormal[mask_points]
Main_abnormal_points['orig_id'] = Main_abnormal_points['PT_ID']
Main_abnormal_points['obj_type'] = 'POINT'


# In[24]:

# merging back together processed parts of the MainOnlyTable
v6_Main_only_processed = pd.concat([Main_normal, Main_abnormal_polygons, Main_abnormal_points])
# renaming columns in the MainTableOnly to match GISInfoTable
v6_Main_only_processed = v6_Main_only_processed.rename(columns={'NAME_PY': 'nm_py', 
                               'NAME_CH':'nm_simp', 
                               'NAME_FT':'nm_trad', 
                               'PRES_LOC':'pres_loc', 
                               'BEG_CHG_TY':'beg_type', 
                               'END_CHG_TY':'end_type', 
                               'TYPE_PY':'type_py',
                               'TYPE_CH':'type_simp',
                               'LEV_RANK':'level',
                               'BEG_YR':'beg_yr',
                               'END_YR':'end_yr',
                               'X_COOR':'x_coord',
                               'Y_COOR':'y_coord'
                              })
# eliminating columns to be dropped in concatenation of DataFrames
v6_Main_only_processed.drop(['BOU_ID', 'BOU_ID_EQUALS_PT_ID','BOU_ID_IN_GISINFO_SYS_ID','BOU_NOTE_ID','ISSUE?','PT_ID', 'PT_ID_IN_GISINFO_SYS_ID', 'PT_NOTE_ID', 'Unnamed: 0'], axis=1, inplace=True)


# In[26]:

# Adding 'sys_id' field that consists of 'hvd_' plus 'orig_id' value
v6_Main_only_processed['sys_id'] = 'hvd_' + v6_Main_only_processed['orig_id'].astype(str)
progress_check(v6_Main_only_processed, '160814_experiment') # PASS


# In[27]:

# joining together GISInfoTable and v6_Main_only_processed
v6_all = pd.concat([v6_GISInfo, v6_Main_only_processed])
# progress_check(v6_all, 'v6_all') # LOOKS GOOD


# In[29]:

# name the result of the union of the v6 GISInfoTable and MainTable "V6_input_draft_20160811.csv"
v6_all.to_csv('output/V6_input_draft_20160811.csv')

