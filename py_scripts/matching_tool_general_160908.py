
# coding: utf-8

# In[1]:

#! /usr/bin/python3

# Script for comparing an input .csv file with an existing .csv file (e.g. the current CHGIS).
# Indicates 1) matches on name and 2) strength of match on content
# Requires the library 'pandas' to be installed, which is included in Anaconda's free Python distribution

# by Stephen Ford (stephen.p.ford@gmail.com)

import pandas as pd
import os.path

# suppressing SettingWithCopyWarning
pd.options.mode.chained_assignment = None  # default='warn'


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
        print("Not a valid filename.  Please try again:")
        name = input()
        
    # checking that the valid filename ends in .csv, prompting for re-entry if not
    while not name.endswith('.csv'):
        print("Filename does not end in .csv -- please try again:")
        name = input()

    print("\nThank you -- filename %s is valid.\n" % name)       
    return pd.read_csv(name, low_memory=False)


# In[3]:

# soliciting files for comparison; presumption is that second file entered will be the CHGIS v5 in .csv format
print("Please input the path of the .csv file (with extension) you wish to compare with the CHGIS:")
new_data = csv_picker()
# /home/sf/chgis/input/sample_data/Donghan_2014-10-02_copy.csv
# /home/sf/chgis/input/sample_data/lexdata.txt.data.csv

print("Please input the path of the .csv file (with extension) containing CHGIS data (script expects v5, or at least its column names):")
chgis = csv_picker()
# /home/sf/chgis/input/v5_augment_2016-08-09.csv


# In[4]:

# initializing list of input_fields (i.e. normalized input fields, called "input_*" in final output)
input_fields = []

# function for mapping the input .csv's fields to the desired, standardized output fields
def field_mapper(normalized_field, frame=new_data, fields=input_fields):
    ''' Function that will prompt user to manually map fields of the input .csv to standardized output fields.
        Name changes will be made in-place (i.e. in the DataFrame -- the .csv will be untouched).
        If user fails to enter anything for the given mapping, the output field will be present in the output 
        file, but have no values.        
    '''
    
    print("\nPlease enter the field in the incoming non-CHGIS .csv that will be labeled '%s' in the output .csv:" % normalized_field)
    orig_field = input()
    
    # prompts for re-entering the input field if 1) it is not one of the column names and 2) it isn't an empty string
    while (not orig_field in list(new_data.columns.values)) and (orig_field):
        print("\nNot a valid column name.  Please try again:")
        orig_field = input()
        
    # simply exit if the user pressed enter, bypassing the mapping, or perform the mapping if a valid field name has been entered
    if orig_field:
        frame.rename(columns={orig_field:normalized_field}, inplace=True)
        fields += [normalized_field]
    return fields


# In[5]:

# declaring the list of output .csv field names that will derive from the new data
# i.e., all those fields whose names will be 'input_*' in the final .csv

normalized_fields = [   
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

for field in normalized_fields:
    input_fields = field_mapper(field)


# In[7]:

# storing to avoid having to reenter stuff later
#han_new_data = new_data
#han_input_fields = input_fields
#han_chgis = chgis

lex_new_data = new_data
lex_input_fields = input_fields
lex_chgis = chgis


# In[ ]:

# only execute to restore from stored data
#new_data = han_new_data
#input_fields = han_input_fields
#chgis = han_chgis

#new_data = lex_new_data
#input_fields = lex_input_fields
#chgis = lex_chgis


# In[8]:

# dropping all fields from the new_data DataFrame that won't be in final output
new_data = new_data[input_fields]

# dropping fields from the new_data DataFrame that weren't mapped
#for field in new_data.columns:
#    if new_data[field].empty:
#        new_data.drop(field, inplace=True)
#        input_fields.remove(field)
        
#print("input_fields are: %s" % str(input_fields))
#print("new_data cols are: %s" % str(new_data.columns))


# In[9]:

# manually renaming one exception to the following pattern
chgis.rename(columns={'src':'data_source'}, inplace=True)

# renaming the CHGIS fields in-place to conform to output specifications
chgis.columns = ['tgaz_%s' % x for x in chgis.columns]


# In[10]:

# offering user choice of strict or fuzzy name-matching

def merge_chooser():
    ''' Function called only if the user selects to merge on traditional characters 繁體字 or simplified characters 简体字
        Lets user choose whether to do a strict or fuzzy merge.
        In a fuzzy merge, only the first two characters of the Chinese names will be checked against one another.
    '''
    print(
    '''
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


# In[11]:

# initializing list of tgaz fields
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


# In[12]:

# soliciting user choice regarding which name field to take as primary
#print(input_fields)

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
    if ((choice == '1') and ('input_nm_trad' in input_fields)):
        print("\nUsing name in complex/traditional Chinese characters 繁体字 as primary matching key.")
        accepted = True
        input_name_match_field = 'input_nm_trad'
        chgis_name_match_field = 'tgaz_nm_trad'
        #output_name_match_field = 'out_nm_trad_match'
        df, name_mode = merge_chooser()
    elif ((choice == '2') and ('input_nm_simp' in input_fields)):
        print("\nUsing name in simplified Chinese characters 简体字 as primary matching key.")
        accepted = True
        input_name_match_field = 'input_nm_simp'
        chgis_name_match_field = 'tgaz_nm_simp'
        #output_name_match_field = 'out_nm_simp_match'
        df, name_mode = merge_chooser()
        #output_fields = [output_name_match_field]
    elif ((choice == '3') and ('input_nm_py' in input_fields)):
        print("\nUsing name in pinyin 拼音 as primary matching key.")
        accepted = True
        input_name_match_field = 'input_nm_py'
        chgis_name_match_field = 'tgaz_nm_py'
        #output_name_match_field = 'out_nm_py_match'
        name_mode = 'strict'
        print('Fuzzy matching is not currently supported for pinyin names.  Proceeding with strict matching.')
        df = chgis.merge(new_data, how='outer', left_on=chgis_name_match_field, right_on=input_name_match_field, indicator=True)
        #df[output_name_match_field] = 
        #output_fields = []
        
    else:
        print("\nNot a valid response.  Please try again, entering a choice corresponding to a valid field:\n")
        choice = input()
        
output_fields = [] # OR [output_name_match_field]                


# In[13]:

#### Abandoning comprehensive for-loop for sake of year matching; manually stringifying coords instead

# converting all fields to strings for ease of comparison
#for field in list(df.columns):
#    df[field] = df[field].astype(str)
spatial_coords = ['input_x_coord', 'input_y_coord', 'tgaz_x_coord', 'tgaz_y_coord']
for field in spatial_coords:
    if (field in input_fields) or (field in tgaz_fields):
        df[field] = df[field].astype(str)


# In[14]:

# removing rows that are only present in the CHGIS file
df = df[df['_merge'] != 'left_only']
df


# In[15]:

def coordinate_matcher(coords, frame=df, fields=output_fields):
    print(
        '''
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
            for coord in coords:
                frame['out_%s_coord_match' % coord] = frame['input_%s_coord' % coord] == frame['tgaz_%s_coord' % coord]
                fields += ['out_%s_coord_match' % coord]
            return "strict"
        elif choice == '2':
            print("Proceeding with fuzzy matching of spatial coordinates.")
            accepted = True
            for coord in coords:
                frame['fuzzy_out_%s_coord_match' % coord] = frame['input_%s_coord' % coord].map(lambda x: x[:3]) == frame['tgaz_%s_coord' % coord].map(lambda x: x[:3])
                fields += ['fuzzy_out_%s_coord_match' % coord]
            return "fuzzy" 
        else:
            print("\nNot a valid response.  Please try again:\n")
            choice = input()


# In[16]:

if ('input_x_coord' in input_fields) and ('input_y_coord' in input_fields):
    coord_mode = coordinate_matcher(['x', 'y'])
elif ('input_x_coord' in input_fields) and not ('input_y_coord' in input_fields):
    coord_mode = coordinate_matcher(['x'])
elif not ('input_x_coord' in input_fields) and ('input_y_coord' in input_fields):
    coord_mode = coordinate_matcher(['y'])
else:
    print("\nNo spatial coordinate fields available for matching.")


# In[17]:

#if (df['input_year_beg'].empty() | df['input_year_end'].empty()):
#    if (df['input_year_beg'].empty()):
#        df.drop(['input_year_beg'])
#        input_fields.remove('input_year_beg')
#        beg_year_matching = False
#    if (df['input_year_end'].empty()):
#        df.drop(['input_year_end'])
#        input_fields.remove('input_year_end')
#        end_year_matching = False

if (not 'input_year_beg' in input_fields) or (not 'input_year_end' in input_fields):
    print("Incoming data lacks a beginning and/or ending year field; no date comparisons will be made.")
else:
    beg_year_matching, end_year_matching = True, True
    
    year_fields = ['input_year_beg', 'input_year_end', 'tgaz_beg', 'tgaz_end']
        
    # in-row match testing
    df['out_beg_match'] = df['input_year_beg'] == df['tgaz_beg']
    df['out_end_match'] = df['input_year_end'] == df['tgaz_end']
        
    # overlap field initialization
    df['out_year_overlap'] = ''

    # converting to strings
    for year_field in year_fields:
        df[year_field] = df[year_field].astype(str)

    #print(df['input_year_beg'])
    #print(df['input_year_beg'].dtype)
    
    # masking so as to separate rows with numeric years from those without
    df['all_numeric'] = df['input_year_beg'].str.isnumeric() & df['input_year_end'].str.isnumeric() & df['tgaz_beg'].str.isnumeric() & df['tgaz_end'].str.isnumeric()
    
    # splitting df into n_df (for numeric) and e_df (for error)
    n_df = df[df['all_numeric']]
    e_df = df[~df['all_numeric']]
    
    ### handling numeric sub-DataFrame
        
    # converting back to numerics from strings
    for year_field in year_fields:
        pd.to_numeric(n_df[year_field], errors='coerce')
    print(n_df['input_year_beg'].dtype)
    
    # replacing non-numeric values in the column with 'NaN' to avoid errors in boolean comparisons below
    #pd.to_numeric(df['input_year_beg'], errors='coerce')
    #pd.to_numeric(df['input_year_end'], errors='coerce')
    #pd.to_numeric(df['tgaz_beg'], errors='coerce')
    #pd.to_numeric(df['tgaz_end'], errors='coerce')
    
    # testing for timespan relationships
    n_df['out_year_overlap'][((n_df['input_year_beg'] == (n_df['tgaz_end'] + 1)) | (n_df['input_year_end'] == (n_df['tgaz_beg'] - 1)))] = 'adjacent'
    n_df['out_year_overlap'][(n_df['input_year_beg'] > n_df['tgaz_beg']) & (n_df['input_year_end'] < n_df['tgaz_end'])] = 'new_nested_in_chgis'
    n_df['out_year_overlap'][(n_df['input_year_beg'] < n_df['tgaz_beg']) & (n_df['input_year_end'] > n_df['tgaz_end'])] = 'chgis_nested_in_new'
    n_df['out_year_overlap'][(n_df['input_year_beg'] < n_df['tgaz_beg']) & (n_df['input_year_end'] > n_df['tgaz_beg']) & (n_df['input_year_end'] < n_df['tgaz_end'])] = 'partial_incl_start'
    n_df['out_year_overlap'][(n_df['input_year_beg'] > n_df['tgaz_beg']) & (n_df['input_year_beg'] < n_df['tgaz_end']) & (n_df['input_year_end'] > n_df['tgaz_end'])] = 'partial_incl_end'
    n_df['out_year_overlap'][(n_df['input_year_beg'] == n_df['tgaz_beg']) & (n_df['input_year_end'] == n_df['tgaz_end'])] = 'perfect_match'
    n_df['out_year_overlap'][(n_df['input_year_beg'] == 0) | (n_df['input_year_end'] == 0) | (n_df['tgaz_beg'] == 0) | (n_df['tgaz_end'] == 0)] = 'CAUTION__ZEROES'
    n_df['out_year_overlap'][(n_df['input_year_beg'] > n_df['input_year_end']) | (n_df['tgaz_beg'] > n_df['tgaz_end'])] = 'ERROR__END_BEFORE_BEG'
    # df['out_year_overlap'][(df['input_year_beg'].isnull()) | (df['input_year_end'].isnull())] = 'ERROR__NON_NUMERIC_DATA'
    df['out_year_overlap'][~df['all_numeric']] = 'ERROR__NON_NUMERIC_YEAR_VALUE'

    ### handling error sub-DataFrame (with non-numeric year values)
    e_df['out_year_overlap'] = 'ERROR__NON_NUMERIC_YEAR_VALUE(S)'
    
    ### concatenating sub-DataFrames back together
    df = pd.concat([n_df, e_df])
    df
    
    # updating output fields
    output_fields += ['out_beg_match'] + ['out_end_match'] + ['out_year_overlap']


# In[18]:

# adding the 'match_strength' column
df['out_content_match_strength'] = 0
output_fields += ['out_content_match_strength']

if ('input_x_coord' in input_fields):
    if coord_mode == "strict":
        df['out_content_match_strength'] += df['out_x_coord_match'].astype(int)
    else: 
        df['out_content_match_strength'] += df['fuzzy_out_x_coord_match'].astype(int)

if ('input_y_coord' in input_fields):
    if coord_mode == "strict":
        df['out_content_match_strength'] += df['out_y_coord_match'].astype(int)
    else: 
        df['out_content_match_strength'] += df['fuzzy_out_y_coord_match'].astype(int)
    
if ('input_beg_year' in input_fields):
    df['out_content_match_strength'] += df['out_beg_match'].astype(int) 
    
if ('input_end_year' in input_fields):
    df['out_content_match_strength'] += df['out_end_match'].astype(int)


# In[19]:

# sorting columns
print(output_fields)
ordered_fields = tgaz_fields + input_fields + ['_merge'] + output_fields
print(ordered_fields)
fuzzy_ordered_fields = ['fuzzy_nm'] + ordered_fields

if name_mode == 'strict':
    df = df[ordered_fields]
else:
    df = df[fuzzy_ordered_fields]


# In[20]:

# replacing 'nan' with '' for improved legibility
df = df.replace('nan', '')


# In[21]:

# outputting results
print('\nData check is complete.  Please input the path (with file extension) to which you want to write the results:\n')
output_path = input()

while not output_path.endswith('.csv'):
        print("Filename does not end in .csv -- please try again or use Ctrl-C to exit:")
        output_path = input()

df.to_csv(output_path)

print('File created at %s.  Now exiting.' % output_path)

