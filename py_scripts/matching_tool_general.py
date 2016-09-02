
# coding: utf-8

# In[1]:

#! /usr/bin/python3

# Script for comparing an input .csv file with an existing .csv file (e.g. the current CHGIS).
# Indicates 1) matches on name and 2) strength of match on content

import pandas as pd
import os.path


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

print("Please input the path of the .csv file (with extension) containing CHGIS data (script expects v5, or at least its column names):")
chgis = csv_picker()


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


# In[9]:

# concatenating the DataFrames together
df = pd.concat([chgis, new_data])


# In[10]:

# converting all fields to strings for ease of comparison
for field in list(df.columns):
    df[field] = df[field].astype(str)


# In[11]:

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
    elif choice == '2':
        print("\nUsing name in simplified Chinese characters 简体字 as primary key.")
        accepted = True
        input_name_match_field = 'input_nm_simp'
        chgis_name_match_field = 'tgaz_nm_simp'
        output_name_match_field = 'out_nm_simp_match'
    elif choice == '3':
        print("\nUsing name in pinyin 拼音 as primary key.")
        accepted = True
        input_name_match_field = 'input_nm_py'
        chgis_name_match_field = 'tgaz_nm_py'
        output_name_match_field = 'out_nm_py_match'
    else:
        print("\nNot a valid response.  Please try again:\n")
        choice = input()


# In[20]:

# function for comparing content fields
def field_matcher(input_field, tgaz_field, out_field, frame):
    ''' Simple function that, within the given pandas DataFrame (`frame`) creates a new 
        field (`indicator_field`) that displays Boolean value indicating whether the given 
        field (`comp_field`)'s value in that row matches at least one other row's value for it. 
    
        Uses a masking procedure -- identify duplicates and uniques, create new DataFrames using 
        the resulting two Boolean series as masks, and then concatenate them back together.
    
        PRESUMES that `frame` is a concatenation of two other DataFrames, each of which initially
        lack any duplicate rows -- that is, if you run this function on either contributing DataFrame,
        with the key field (e.g. `sys_id`) as `comp_field`, it will find no matches whatsoever
    '''
    
    mask_duplicates = frame.duplicated(subset=[input_field, tgaz_field], keep=False)
    mask_uniques = ~mask_duplicates
    duplicates = frame[mask_duplicates]
    duplicates[out_field] = True
    uniques = frame[mask_uniques]
    uniques[out_field] = False
    frame = pd.concat([duplicates, uniques])
    frame
    return frame


# In[21]:

# performing the match checks
df_one = field_matcher(input_name_match_field, chgis_name_match_field, output_name_match_field, df)
df_two = field_matcher('input_x_coord', 'tgaz_x_coord', 'out_x_coord_match', df_one)
df_three = field_matcher('input_y_coord', 'tgaz_y_coord', 'out_y_coord_match', df_two)
df_four = field_matcher('input_year_beg', 'tgaz_beg', 'out_beg_match', df_three)
df_final = field_matcher('input_year_end', 'tgaz_end', 'out_end_match', df_four)


# In[23]:

# adding the 'match_strength' column
df_final['out_content_match_strength'] = df_final['out_x_coord_match'].astype(int) + df_final['out_y_coord_match'].astype(int) + df_final['out_beg_match'].astype(int) + df_final['out_end_match'].astype(int)


# In[38]:

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

ordered_fields = tgaz_fields + input_fields + [output_name_match_field] + ['out_x_coord_match'] + ['out_y_coord_match'] + ['out_beg_match'] + ['out_end_match'] + ['out_content_match_strength']
df_final = df_final[ordered_fields]


# In[36]:

# replacing 'nan' with '' for improved legibility
df_final = df_final.replace('nan', '')


# In[37]:

# outputting results
print('\nData check is complete.  Please input the path (with file extension) to which you want to write the results:\n')
output_path = input()

while not output_path.endswith('.csv'):
        print("Filename does not end in .csv -- please try again or use Ctrl-C to exit:")
        output_path = input()

df_final.to_csv(output_path)

print('File created at %s.  Now exiting.' % output_path)

