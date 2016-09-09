
# coding: utf-8

# In[15]:

#! /usr/bin/python3

# Script for comparing an input .csv file with an existing .csv file (e.g. the current CHGIS).
# Indicates 1) matches on name and 2) strength of match on content
# Requires the library 'pandas' to be installed, which is included in Anaconda's free Python distribution

# by Stephen Ford (stephen.p.ford@gmail.com)

import pandas as pd
import os.path

### TODO: 
# DONE -- 1. year overlap
# 2. CLI flags


# In[2]:

# function for selecting .csv files for manipulation

def csv_picker():
    ''' Function for checking whether user input path 1) is that of a valid file, and 2) is of a file ending with '.csv'
        Prompts for re-entry if entry is invalid.
        Returns a pandas DataFrame constructed from the valid .csv file
    '''
    name = input()

    # checking that the path is a valid filename, and prompting for re-entry if not
    while not (os.path.isfile(name)):
        print("Not a valid filename.  Please try again, or use Ctrl-C to exit:")
        name = input()
        
    # checking that the valid filename ends in .csv, prompting for re-entry if not
    while not name.endswith('.csv'):
        print("Filename does not end in .csv -- please try again or use Ctrl-C to exit:")
        name = input()

    print("\nThank you -- filename %s is valid.\n" % name)       
    return pd.read_csv(name, low_memory=False)


# In[3]:

# soliciting files for comparison; presumption is that second file entered will be the CHGIS v5 in .csv format
print("Please input the path of the .csv file (with extension) you wish to compare with the CHGIS:")
new_data = csv_picker()
# /home/sf/chgis/input/sample_data/Donghan_2014-10-02_copy.csv

print("Please input the path of the .csv file (with extension) containing CHGIS data (script expects v5, or at least its column names):")
chgis = csv_picker()
# /home/sf/chgis/input/v5_augment_2016-08-09.csv


# In[4]:

# function for mapping the input .csv's fields to the desired, standardized output fields
def field_mapper(output_field, frame=new_data):
    ''' Function that will prompt user to manually map fields of the input .csv to standardized output fields.
        Name changes will be made in-place (i.e. in the DataFrame -- the .csv will be untouched).
        If user fails to enter anything for the given mapping, the output field will be present in the output 
        file, but have no values.        
    '''
    
    print("\nPlease enter the field in the incoming non-CHGIS .csv that will be labeled '%s' in the output .csv:" % output_field)
    input_field = input()
    
    # prompts for re-entering the input field if 1) it is not one of the column names and 2) it isn't an empty string
    while (not input_field in list(new_data.columns.values)) and (input_field):
        print("\nNot a valid column name.  Please try again:")
        input_field = input()
        
    # simply exit if the user pressed enter, bypassing the mapping, or perform the mapping if a valid field name has been entered
    if input_field:
        frame.rename(columns={input_field:output_field}, inplace=True)
    else:
        frame[output_field] = ''        


# In[5]:

# declaring the list of output .csv field names that will derive from the new data
# i.e., all those fields whose names will be 'input_*' in the final .csv

input_fields = [   
    'input_id',
    'input_nm_py',
    'input_nm_simp',
    'input_nm_trad',
    'input_type',
    'input_year_beg',
    'input_year_end',
    'input_dynasty',
    'input_other_id',
    'input_prnt',
    'input_obj_type',
    'input_x_coord',
    'input_y_coord'
]


# In[6]:

# renaming fields in the new data DataFrame to conform to specifications

for field in input_fields:
    field_mapper(field)


# In[7]:

# dropping all fields from the new_data DataFrame that won't be in final output
new_data = new_data[input_fields]


# In[8]:

# manually renaming one exception to the following pattern
chgis.rename(columns={'src':'data_source'}, inplace=True)

# renaming the CHGIS fields in-place to conform to output specifications
chgis.columns = ['tgaz_%s' % x for x in chgis.columns]


# In[64]:

# offering user choice of strict or fuzzy name-matching

def merge_chooser():
    ''' Function called only if the user selects to merge on traditional characters 繁體字 or simplified characters 简体字
        Lets user choose whether to do a strict or fuzzy merge.
        In a fuzzy merge, only the first two characters of the Chinese names will be checked against one another.
    '''
    print('''
        Please indicate, by entering a numerical digit 1-2, whether you wish to do a strict or fuzzy match of names:
        1. Strict matching (e.g. '張掖' matches '張掖', but '張掖' does not match '張掖居延屬國')
        2. Fuzzy matching (e.g. '張掖' matches '張掖', and '張掖' also matches '張掖居延屬國')
        ''')

    accepted = False
    choice = input()

    while accepted == False:
        if choice == '1':
            print('Proceeding with strict matching of names.')
            accepted = True
            mode = 'strict'
            df = chgis.merge(new_data, how='outer', left_on=chgis_name_match_field, right_on=input_name_match_field, indicator=True)
            return df, mode
        elif choice == '2':
            print('Proceeding with fuzzy matching of names.')
            accepted = True
            mode = 'fuzzy'
            chgis['fuzzy_nm'] = chgis[chgis_name_match_field].map(lambda x: x[:2])
            new_data['fuzzy_nm'] = new_data[input_name_match_field].map(lambda x: x[:2])
            df = chgis.merge(new_data, how='outer', on='fuzzy_nm', indicator=True)
            return df, mode
        else:
            print("\nNot a valid response.  Please try again:\n")
            choice = input()


# In[74]:

# soliciting user choice regarding which name field to take as primary
print(
    '''
    Thank you. Now, please indicate, by entering a numerical digit 1-3, which of the following names you wish to make the primary key for comparing data:
    1. Name in complex/traditional Chinese characters 繁体字
    2. Name in simplified Chinese characters 简体字
    3. Name in pinyin 拼音
    '''
)

accepted = False
choice = input()

while accepted == False:
    if choice == '1':
        print("\nUsing name in complex/traditional Chinese characters 繁体字 as primary key.")
        accepted = True
        input_name_match_field = 'input_nm_trad'
        chgis_name_match_field = 'tgaz_nm_trad'
        output_name_match_field = 'out_nm_trad_match'
        df, mode = merge_chooser()
        
    elif choice == '2':
        print("\nUsing name in simplified Chinese characters 简体字 as primary key.")
        accepted = True
        input_name_match_field = 'input_nm_simp'
        chgis_name_match_field = 'tgaz_nm_simp'
        output_name_match_field = 'out_nm_simp_match'
        df, mode = merge_chooser()
    elif choice == '3':
        print("\nUsing name in pinyin 拼音 as primary key.")
        accepted = True
        input_name_match_field = 'input_nm_py'
        chgis_name_match_field = 'tgaz_nm_py'
        output_name_match_field = 'out_nm_py_match'
        mode = 'strict'
        print('Fuzzy matching is not currently supported for pinyin names.  Proceeding with strict matching.')
        df = chgis.merge(new_data, how='outer', left_on=chgis_name_match_field, right_on=input_name_match_field, indicator=True)
    else:
        print("\nNot a valid response.  Please try again:\n")
        choice = input()


# In[75]:

#### Abandoning comprehensive for-loop for sake of year matching; manually stringifying coords instead

# converting all fields to strings for ease of comparison
#for field in list(df.columns):
#    df[field] = df[field].astype(str)
spatial_coords = ['input_x_coord', 'input_y_coord', 'tgaz_x_coord', 'tgaz_y_coord']
for field in spatial_coords:
    df[field] = df[field].astype(str)


# In[76]:

# removing rows that are only present in the CHGIS file
df = df[df['_merge'] != 'left_only']


# In[77]:

# asking user if they want to do strict or fuzzy matching on spatial coordinates
print('''
    Please indicate, by entering a numerical digit 1-2, whether you wish to do a strict or fuzzy match of spatial coordinates:
    1. Strict matching (requires exact match, e.g. '119.64656' does NOT match '119.646560', '119.64657', or '119.325')
    2. Fuzzy matching (only requires that truncated number of whole degrees matches, e.g. '119.64656' DOES match '119.646560', '119.64657', and '119.325')
    ''')

accepted = False
choice = input()

while accepted == False:
    if choice == '1':
        print('Proceeding with strict matching of spatial coordinates.')
        accepted = True
        df['out_x_coord_match'] = df['input_x_coord'] == df['tgaz_x_coord']
        df['out_y_coord_match'] = df['input_y_coord'] == df['tgaz_y_coord']

    elif choice == '2':
        print('Proceeding with fuzzy matching of spatial coordinates.')
        accepted = True
        df['out_x_coord_match'] = df['input_x_coord'].map(lambda x: x[:3]) == df['tgaz_x_coord'].map(lambda x: x[:3])
        df['out_y_coord_match'] = df['input_y_coord'].map(lambda x: x[:3]) == df['tgaz_y_coord'].map(lambda x: x[:3])

    else:
        print("\nNot a valid response.  Please try again:\n")
        choice = input()


# In[78]:

# in-row match testing
df['out_beg_match'] = df['input_year_beg'] == df['tgaz_beg']
df['out_end_match'] = df['input_year_end'] == df['tgaz_end']

# overlap testing
df['out_year_overlap'] = ''

df['out_year_overlap'][(df['input_year_beg'] > df['tgaz_beg']) & (df['input_year_end'] < df['tgaz_end'])] = 'new_nested_in_chgis'
df['out_year_overlap'][(df['input_year_beg'] < df['tgaz_beg']) & (df['input_year_end'] > df['tgaz_end'])] = 'chgis_nested_in_new'
df['out_year_overlap'][(df['input_year_beg'] < df['tgaz_beg']) & (df['input_year_end'] > df['tgaz_beg']) & (df['input_year_end'] < df['tgaz_end'])] = 'partial_incl_start'
df['out_year_overlap'][(df['input_year_beg'] > df['tgaz_beg']) & (df['input_year_beg'] < df['tgaz_end']) & (df['input_year_end'] > df['tgaz_end'])] = 'partial_incl_end'
df['out_year_overlap'][(df['input_year_beg'] == df['tgaz_beg']) & (df['input_year_end'] == df['tgaz_end'])] = 'perfect_match'
df['out_year_overlap'][(df['input_year_beg'] == 0) | (df['input_year_end'] == 0) | (df['tgaz_beg'] == 0) | (df['tgaz_end'] == 0)] = 'CAUTION'
df['out_year_overlap'][(df['input_year_beg'] > df['input_year_end']) | (df['tgaz_beg'] > df['tgaz_end'])] = 'ERROR'


# In[79]:

# adding the 'match_strength' column
df['out_content_match_strength'] = df['out_x_coord_match'].astype(int) + df['out_y_coord_match'].astype(int) + df['out_beg_match'].astype(int) + df['out_end_match'].astype(int)


# In[80]:

# sorting columns
tgaz_fields = [
    'tgaz_sys_id',
    'tgaz_nm_py',
    'tgaz_nm_simp',
    'tgaz_nm_trad',
    'tgaz_beg',
    'tgaz_end',
    'tgaz_data_source',
    'tgaz_obj_type',
    'tgaz_pres_loc',
    'tgaz_prnt_id',
    'tgaz_prnt_py',
    'tgaz_prnt_simp',
    'tgaz_prnt_sysid',
    'tgaz_type_ch',
    'tgaz_type_py',
    'tgaz_x_coord',
    'tgaz_y_coord'
]

ordered_fields = tgaz_fields + input_fields + ['_merge'] + ['out_x_coord_match'] + ['out_y_coord_match'] + ['out_beg_match'] + ['out_end_match'] + ['out_year_overlap'] + ['out_content_match_strength']
fuzzy_ordered_fields = ['fuzzy_nm'] + ordered_fields

if mode == 'strict':
    df = df[ordered_fields]
else:
    df = df[fuzzy_ordered_fields]


# In[81]:

# replacing 'nan' with '' for improved legibility
df = df.replace('nan', '')


# In[82]:

# outputting results
print('\nData check is complete.  Please input the path (with file extension) to which you want to write the results:\n')
output_path = input()

while not output_path.endswith('.csv'):
        print("Filename does not end in .csv -- please try again or use Ctrl-C to exit:")
        output_path = input()

df.to_csv(output_path)

print('File created at %s.  Now exiting.' % output_path)

