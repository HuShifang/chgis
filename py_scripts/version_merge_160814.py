
# coding: utf-8

# In[1]:

import pandas as pd
from pandas import Series, DataFrame
import numpy as np


# In[2]:

# importing v5 and v6 tables as DataFrames
v5 = pd.read_csv('input/v5_augment_2016-08-09.csv', low_memory=False)
v6 = pd.read_csv('input/V6_input_draft_20160811.csv', low_memory=False)
v5['version'] = 5
v6['version'] = 6


# In[3]:

# merge v5 and v6 into a single DataFrame
df = pd.concat([v5,v6])
df.to_csv('output/v5_and_v6.csv')


# In[4]:

# check merged df for duplicates by sys_id, generate file with tagging
mask_duplicates = df.duplicated(subset='sys_id', keep=False)
mask_uniques = ~mask_duplicates
duplicates = df[mask_duplicates]
duplicates['sys_id_duplicate'] = True
uniques = df[mask_uniques]
uniques['sys_id_duplicate'] = False
df_two = pd.concat([duplicates, uniques])
df_two.to_csv('output/v5_and_v5_duplicates_and_uniques.csv')

### following lines would output csv's containing only the duplicates and uniques
duplicates.to_csv('output/v5_and_v6_primary_duplicates.csv')
#uniques.to_csv('v5_and_v6_uniques.csv')


# In[5]:

# function for adding Boolean flags as fields to the DataFrame file
def field_matcher(frame, v6_field, v5_field, new_field):
    mask_duplicates = frame.duplicated(subset=[v6_field, v5_field], keep=False)
    mask_uniques = ~mask_duplicates
    duplicates = frame[mask_duplicates]
    duplicates[new_field] = True
    uniques = frame[mask_uniques]
    uniques[new_field] = False
    return pd.concat([duplicates, uniques])        


# In[8]:

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


# In[9]:

df_thirteen.to_csv('output/V5andV6_output.csv')

