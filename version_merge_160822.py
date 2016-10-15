
# coding: utf-8

# In[2]:

#! /usr/bin/python3
# 
# /version_merge_160822.ipynb
# /py_scripts/version_merge_160822.py
#
# A script for checking data integrity of CHGIS v5 and v6.  
# The script takes a v5 .csv provided by Lex Berman and a v6 .csv generated using v6_consolidation_160814.ipynb (or the same-name .py script)
# The .csv files are internally unique -- that is, there are no duplicate items within them -- and have several (but not all) fields in common
# This script checks for duplicates between them, based on various fields including 'sys_id'
# Columns containing Boolean values are appended to the end of rows, indicating whether fields are duplicates or not
# There are several "meta" columns at the end, marking out rows that may be of interest
# Note that while there are several rows where all relevant data save for 'sys_id' match, there do not appear to be any where only the 'sys_id' matches
# The script has not been fully refactored, and can yet be optimized; however, it should still run relatively quickly.
# Three .csv files are output -- one containing the entirety of both v5 and v6 together, one containing just v5 rows, and one containing just v6 rows

import pandas as pd
from pandas import Series, DataFrame
import numpy as np


# In[3]:

# importing v5 and v6 tables as DataFrames
v5 = pd.read_csv('input/v5_augment_2016-08-09.csv', low_memory=False)
v6 = pd.read_csv('input/V6_input_draft_20160811.csv', low_memory=False)

# creating a field indicating which version of CHGIS the given row came from
v5['version'] = 5
v6['version'] = 6


# In[4]:

# merge v5 and v6 into a single DataFrame
df = pd.concat([v5,v6])


# In[5]:

# check merged df for duplicates by sys_id, generate file with tagging
mask_duplicates = df.duplicated(subset='sys_id', keep=False)
mask_uniques = ~mask_duplicates
duplicates = df[mask_duplicates]
duplicates['sys_id_duplicate'] = True
uniques = df[mask_uniques]
uniques['sys_id_duplicate'] = False
df_two = pd.concat([duplicates, uniques])
df_two.to_csv('output/v5_and_v5_duplicates_and_uniques.csv')

### following lines would output .csv's containing only the duplicates and uniques
#duplicates.to_csv('output/v5_and_v6_primary_duplicates.csv')
#uniques.to_csv('v5_and_v6_uniques.csv')


# In[6]:

# function for adding Boolean flags as fields to the DataFrame file
def field_matcher(frame, v6_field, v5_field, new_field):
    '''Simple function for comparing the specified fields from versions 5 and 6 of the CHGIS within the specified composite frame, outputting the Boolean result to a new field.  
    Assumes that the CHGIS versions' tables which have been concatenated into the frame are already internally unique, i.e. that any matches found will be between versions, not within.  
    Rather than iterate over rows, creates a Series of Boolean values which serves as a sort of mask for filtering out rows with duplicate and unique values in the specified fields. -- SF, 160817'''
    mask_duplicates = frame.duplicated(subset=[v6_field, v5_field], keep=False)
    mask_uniques = ~mask_duplicates
    duplicates = frame[mask_duplicates]
    duplicates[new_field] = True
    uniques = frame[mask_uniques]
    uniques[new_field] = False
    return pd.concat([duplicates, uniques])        


# In[7]:

# performing duplicate checks field-by-field per 'Match_fields_from_V6_to_V5.csv'
df_three = field_matcher(df_two, 'nm_py', 'nm_py', 'nm_py_duplicate')
df_four = field_matcher(df_three, 'nm_simp', 'nm_simp', 'nm_simp_duplicate')
df_five = field_matcher(df_four, 'nm_trad', 'nm_trad', 'nm_trad_duplicate')

# trying to workaround failure to recognize matches
df_five['x_coord'] = df_five['x_coord'].astype(str)
df_five['y_coord'] = df_five['y_coord'].astype(str)
df_six = field_matcher(df_five, 'x_coord', 'x_coord', 'x_coord_duplicate')
df_seven = field_matcher(df_six, 'y_coord', 'y_coord', 'y_coord_duplicate')
df_seven['x_coord'] = df_seven['x_coord'].astype(float)
df_seven['y_coord'] = df_seven['y_coord'].astype(float)

# resuming secondary checks
df_eight = field_matcher(df_seven, 'pres_loc', 'pres_loc', 'pres_loc_duplicate')
df_nine = field_matcher(df_eight, 'type_py', 'type_py', 'type_py_duplicate')
df_ten = field_matcher(df_nine, 'type_simp', 'type_ch', 'type_simp/ch_duplicate')
df_eleven = field_matcher(df_ten, 'beg_yr', 'beg', 'beg_yr_duplicate')
df_twelve = field_matcher(df_eleven, 'end_yr', 'end', 'end_yr_duplicate')
df_thirteen = field_matcher(df_twelve, 'obj_type', 'obj_type', 'obj_type_duplicate')
df_thirteen['exact_match'] = df_thirteen.all(axis=1, bool_only=True)


# In[10]:

### creating new columns for ease of filtering

# NOTE that this can probably be refactored to use a slice of df_thirteen columns; 
# I was having problems slicing it right, however, so I used this less elegant approach, explicitly checking each field's value
# The script runs sufficiently quickly as-is, however

# Note that numpy.where() is used here, and NOT pandas.where() 

## if 'sys_id_duplicate' == False, but the other duplicate fields == True, then 'content_only' = True
df_thirteen['content_only'] = np.where(
    ((df_thirteen['sys_id_duplicate'] == False) &
    ((df_thirteen['nm_py_duplicate'] == True) & 
    (df_thirteen['nm_simp_duplicate'] == True) & 
    (df_thirteen['nm_trad_duplicate'] == True) &
    (df_thirteen['x_coord_duplicate'] == True) &
    (df_thirteen['y_coord_duplicate'] == True) &
    (df_thirteen['pres_loc_duplicate'] == True) &
    (df_thirteen['type_py_duplicate'] == True) &
    (df_thirteen['type_simp/ch_duplicate'] == True) &
    (df_thirteen['beg_yr_duplicate'] == True) &
    (df_thirteen['end_yr_duplicate'] == True) &
    (df_thirteen['obj_type_duplicate'] == True))), 'True', 'False') 

## if 'sys_id'duplicate' == True, but the other duplicate fields == False, then 'id_only' = True
df_thirteen['id_only'] = np.where(
    ((df_thirteen['sys_id_duplicate'] == True) & 
    ((df_thirteen['nm_py_duplicate'] == False) & 
    (df_thirteen['nm_simp_duplicate'] == False) & 
    (df_thirteen['nm_trad_duplicate'] == False) &
    (df_thirteen['x_coord_duplicate'] == False) &
    (df_thirteen['y_coord_duplicate'] == False) &
    (df_thirteen['pres_loc_duplicate'] == False) &
    (df_thirteen['type_py_duplicate'] == False) &
    (df_thirteen['type_simp/ch_duplicate'] == False) &
    (df_thirteen['beg_yr_duplicate'] == False) &
    (df_thirteen['end_yr_duplicate'] == False) &
    (df_thirteen['obj_type_duplicate'] == False))), 'True', 'False') 

df_final = df_thirteen


# In[11]:

# outputting .csv with v5 AND v6
df_final.to_csv('output/V5andV6_output.csv')

# masking, outputting v5 alone
v5_mask = df_final['version'] == 5
v5_final = df_final[v5_mask]
v5_final.to_csv('output/V5_output.csv')

# masking, outputting v6 alone
v6_mask = df_final['version'] == 6
v6_final = df_final[v6_mask]
v6_final.to_csv('output/V6_output.csv')

