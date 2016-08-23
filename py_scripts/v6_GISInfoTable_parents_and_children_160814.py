
# coding: utf-8

# In[2]:

#! /usr/bin/python3
#
# /v6_GISInfoTable__parents_and_children_160814.ipynb
# /py_scripts/v6_GISInfoTable__parents_and_children_160814.py
#
# An experimental script for counting the number of parent rows in PartOf table (from CHGIS v6 .mdb file provided by Fudan 复旦) that each row in the GISInfo table has

import pandas as pd
from pandas import Series, DataFrame
import numpy as np


# In[3]:

# import tables as DataFrames
GISInfo = pd.read_csv('input/v6_GISInfoTable_2016-08-09.csv')
PartOf = pd.read_csv('input/PartOf.csv')


# In[19]:

# count the number of parent rows in PartOf table that each row in GISInfo table has
# i.e., count how many different 'PRT_ID' there are for a particular 'CHILD_ID' == 'mdb_id', and append it to the GISInfoTable

# generating column that gives total count of # of parents for each row based on 'CHILD_ID'
PartOf['parent_counts'] = PartOf.groupby(['CHILD_ID'])['PRT_ID'].transform('count')

# drop duplicates in preparation for merge
PartOf_no_duplicates = PartOf.drop_duplicates(['CHILD_ID'])

# cut unneeded cols and rename for merge
PartOf_no_duplicates.drop(['CHILD_NMPY','CHILD_NMCH','CHILD_NMFT','BEG_YR','END_YR','PRT_NMPY','PRT_NMCH','PRT_ID'], axis=1, inplace=True)
PartOf_no_duplicates = PartOf_no_duplicates.rename(columns={'CHILD_ID':'mdb_id'})

# combine 
final = pd.merge(GISInfo, PartOf_no_duplicates, on='mdb_id')

# write result
final.to_csv('output/v6_GISInfoTable_with_parents_2016-08-14.csv')

