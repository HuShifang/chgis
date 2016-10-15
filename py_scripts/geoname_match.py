
# coding: utf-8

# In[1]:

#! /usr/bin/python3

# Script for comparing an incoming .csv file with a target .csv file (e.g. the CHGIS).
# Matches primarily on name, but optionally on other fields too
# Only non-core library used is pandas, which can be installed via pip or as part of a Python distribution (e.g. Anaconda)
# by Stephen Ford (stephen.p.ford@gmail.com)

import pandas as pd
from datetime import datetime
from collections import OrderedDict
from pprint import pprint
import os.path

# suppressing SettingWithCopyWarning
pd.options.mode.chained_assignment = None  # default='warn'


# In[2]:

### Initializing the lists and dictionaries that will be used:
# 1. to map the fields in the incoming and target .csv files to the standard output fields
# 2. to drop the standard output fields that the user chooses not to use
# 3. to put the final output fields into their desired, standard order

# initializing list of incoming_fields 
incoming_fields = []

# defining ordered dictionary that stores the standard incoming field names along with a natural English description, for use in user prompts
incoming_description = OrderedDict([
    ('input_id', 'a unique ID'),
    ('input_nm_py',"a name in pinyin"),
    ('input_nm_simp',"a name in simplified Chinese characters (简体字)"),
    ('input_nm_trad',"a name in traditional Chinese characters (繁體字)"),
    ('input_type_py',"an administrative type in pinyin (e.g. 'Xian')"),
    ('input_type_ch',"an administrative type in Chinese (simplified) characters (e.g. '县')"),
    ('input_year_beg',"a beginning year"),
    ('input_year_end',"an ending year"),
    ('input_dynasty',"a dynasty"),
    ('input_other_id',"another, alternate unique ID"),
    ('input_prnt',"the parent administrative unit's name"),
    ('input_obj_type',"a geospatial type (Point/Vector/Polygon)"),
    ('input_x_coord',"an x coordinate"),
    ('input_y_coord',"a y coordinate")
])
    
# initializing ordered dictionary that will store the original .csv's fields and what they're renamed in the final output as key-value pairs 
incoming_mapping = OrderedDict([])

# declaring the list of output .csv field names that will derive from the new data
# i.e., all those fields whose names will be 'input_*' in the final .csv
final_incoming_fields = list(incoming_description.keys())

# initializing list of actual target fields
target_fields = []

# initializing list of default target CHGIS v5 fields (taken from v5_augment_2016-08-09.csv), for use in automated renaming
default_target_fields_v5 = [
    'seq', 
    'sys_id', 
    'src', 
    'nm_py', 
    'nm_simp', 
    'nm_trad', 
    'x_coord', 
    'y_coord', 
    'pres_loc', 
    'type_py', 
    'type_ch', 
    'beg', 
    'end', 
    'obj_type',
    'prnt_id', 
    'prnt_sysid', 
    'prnt_simp', 
    'prnt_py'
]

# initializing list of default target CHGIS v6 fields (taken from V6_input_draft_20160811.csv), for use in automated renaming
default_target_fields_v6 = [
 'beg_rule',
 'beg_type',
 'beg_yr',
 'checker',
 'compiler',
 'end_rule',
 'end_type',
 'end_yr',
 'entry_date',
 'filename',
 'geo_comp',
 'geo_src',
 'level',
 'mdb_id',
 'nm_py',
 'nm_simp',
 'nm_trad',
 'note_id',
 'obj_type',
 'orig_id',
 'pres_loc',
 'sys_id',
 'type_py',
 'type_simp',
 'x_coord',
 'y_coord'
]

# defining ordered dictionary that stores the standard target field names along with a natural English description, for use in user prompts
target_description = OrderedDict([
    ('tgaz_sys_id','a unique ID'),
    ('tgaz_nm_py', "a name in pinyin"),
    ('tgaz_nm_simp',"a name in simplified Chinese characters (简体字)"),
    ('tgaz_nm_trad',"a name in traditional Chinese characters (繁體字)"),
    ('tgaz_beg',"a beginning year"),
    ('tgaz_end',"an ending year"),
    ('tgaz_data_source', "the source of the data"),
    ('tgaz_obj_type',"a geospatial type (Point/Vector/Polygon)"),
    ('tgaz_pres_loc',"the place's present-day name"),
    ('tgaz_prnt_id',"the parent administrative unit's unique ID (NOT prefixed 'hvd_')"),
    ('tgaz_prnt_py',"the parent administrative unit's name in pinyin"),
    ('tgaz_prnt_simp',"the parent administrative unit's name in simplified Chinese characters (简体字)"),
    ('tgaz_prnt_sysid',"the parent administrative unit's unique ID (prefxed 'hvd_')"),
    ('tgaz_type_ch',"an administrative type in Chinese (simplified) characters (e.g. 县)"),
    ('tgaz_type_py',"an administrative type in pinyin (e.g. 'Xian')"),
    ('tgaz_x_coord',"an x coordinate"),
    ('tgaz_y_coord',"a y coordinate")
])

# initializing dictionary that will store as key-value pairs the original target .csv's fields and what they're renamed in the final output
target_mapping = OrderedDict([])

# initializing list of tgaz fields (i.e. the standardized output-form of the CHGIS fields)
final_target_fields = list(target_description.keys())


# In[3]:

# function for selecting .csv files for manipulation
def csv_picker():
    ''' Function for checking whether user input path 1) is that of a valid file, and 2) is of a file ending with '.csv'
        Prompts for re-entry if entry is invalid.
        Returns a pandas DataFrame constructed from the valid .csv file
    '''
    path_name = input()

    # checking that the path is a valid filename, and prompting for re-entry if not
    while not (os.path.isfile(path_name)):
        print("Not a valid filename.  Please try again:")
        path_name = input()
        
    # checking that the valid filename ends in .csv, prompting for re-entry if not
    while not path_name.endswith('.csv'):
        print("Filename does not end in .csv -- please try again:")
        path_name = input()

    print("\nThank you -- path %s is valid.\n" % path_name)
    
    # storing only the file's basename, for use in user prompts
    name = os.path.basename(path_name)
    return pd.read_csv(path_name, low_memory=False), name


# In[4]:

# function for mapping the input .csv's fields to the desired, standardized output fields
def field_mapper(std_field, std_field_description, frame, fields, name, mapping):
    ''' Function that will prompt user to manually map fields of the input .csv to standardized output fields.
        Name changes will be made in-place (i.e. in the DataFrame -- the .csv will be untouched).
        If user fails to enter anything for the given mapping, that field will dropped from the final output file.        
    '''
    
    print("\nPlease enter the field of the incoming file %s that contains %s (this will be renamed '%s' in the output .csv):" % (name, std_field_description, std_field))
    orig_field = input()
    
    # prompts for re-entering the input field if 1) it is not one of the column names and 2) it isn't an empty string
    while (not orig_field in list(frame.columns)) and (orig_field):
        print("\nNot a valid column name.  Please try again:")
        orig_field = input()
        
    # simply exit if the user pressed enter, bypassing the mapping, or perform the mapping if a valid field name has been entered
    if orig_field:
        mapping.update({orig_field:std_field})
        frame.rename(columns={orig_field:std_field}, inplace=True)
        fields += [std_field]
    return fields, mapping


# In[5]:

def name_checker(name_fields, fields, prefix, frame):
    ''' Function will confirm that at least one name field has been entered, and prompt user to remap the three
        name fields until at least one is a valid entry. Updates the DataFrame in-place and returns the updated field list.
    '''
    
    while (((name_fields[0] in fields) or (name_fields[1] in fields) or (name_fields[2] in fields)) == False):
        print("At least one name field needs to be specified. Please try again.")
        # counter ensures that name fields are inserted at correct place in sequence
        counter = 1
        for name_field in name_fields:
            print("Please enter the field that will be labeled '%s' in the output .csv:" % name_field)
            orig_field = input()
            if orig_field:
                if (orig_field in list(frame.columns)):
                    frame.rename(columns={orig_field:name_field}, inplace=True)
                    fields.insert(counter, name_field)
                    counter+=1
                else: 
                    print("Input not accepted -- field not found in data.")
    return fields
               


# In[6]:

# offering user choice of strict or fuzzy name-matching

def merge_chooser(target_field, incoming_field):
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
            df = target.merge(incoming, how='outer', left_on=target_field, right_on=incoming_field, indicator=True)
            return df, mode
        elif choice == '2':
            print('Proceeding with fuzzy matching of names.')
            accepted = True
            mode = 'fuzzy'
            target['fuzzy_nm'] = target[target_field].map(lambda x: str(x)[:2])
            incoming['fuzzy_nm'] = incoming[incoming_field].map(lambda x: str(x)[:2])
            df = target.merge(incoming, how='outer', on='fuzzy_nm', indicator=True)
            return df, mode
        else:
            print("\nNot a valid response.  Please try again:\n")
            choice = input()


# In[7]:

def coordinate_matcher(coords, frame, fields):
    ''' Function that performs a strict or fuzzy matching of spatial coordinates.  Returns a string indicating the type of match performed.
        The matches' results are added to the DataFrame within the function.
    '''
    
    print('''
Please indicate, by entering a numerical digit 1-2, whether you wish to do a strict or fuzzy match of spatial coordinates:
    1. Strict matching (requires exact match, e.g. '119.64656' does NOT match '119.646560', '119.64657', or '119.325')
    2. Fuzzy matching (requires only that rounded numbers match -- you specify the number of decimal places)
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
            decimal_place = None
            return "strict", decimal_place
        elif choice == '2':
            print("Proceeding with fuzzy matching of spatial coordinates.")
            accepted = True
            print('''
Please enter a number indicating the number of decimal places to which to round the decimal coordinate value.
     For example, if you enter 0, 117.91 and 118.08 will round to 118 and match; if you enter 1, 117.91 will round to 117.9 and 118.08 will round to 118.1, and they won't match.
     Be advised that coordinates rarely have more than 7 decimal places of precision.
                  ''')
            decimal_place = input()
            try: 
                for coord in coords:
                    frame['fuzzy_out_%s_coord_match' % coord] = frame['input_%s_coord' % coord].map(lambda x: round(x, int(decimal_place))) == frame['tgaz_%s_coord' % coord].map(lambda x: round(x, int(decimal_place)))
                    fields += ['fuzzy_out_%s_coord_match' % coord]
                return "fuzzy", decimal_place
                                                                                                
            except:
                print("Not a valid response. Defaulting to 0 (integer-rounding).")
                for coord in coords:
                    frame['fuzzy_out_%s_coord_match' % coord] = frame['input_%s_coord' % coord].map(lambda x: round(x, 0)) == frame['tgaz_%s_coord' % coord].map(lambda x: round(x, 0))
                    fields += ['fuzzy_out_%s_coord_match' % coord]
                return "fuzzy", decimal_place
        else:
            print("\nNot a valid response.  Please try again:\n")
            choice = input()


# In[8]:

def title_caser(fields, actual_fields, frame):
    '''Very simple function that title-cases the contents of the given fields, provided that they are actually used in the DataFrame 
    '''   
    for field in fields:
        if field in actual_fields:
            frame[field] = frame[field].map(lambda x: str(x).title())


# In[9]:

# soliciting files for comparison; presumption is that second file entered will be the CHGIS v5 in .csv format
print("Please type the path of the incoming .csv file (with extension):")
incoming, incoming_name = csv_picker()

print("Please type the path of the target .csv file (with extension):")
target, target_name = csv_picker()


# In[10]:

### presenting user with choice of a default mapping of CHGIS fields (based on v5_augment_2016-08-09.csv) or of manually entering their own mapping

print('''Please indicate by entering '1' or '2' whether you wish to use a default mapping of CHGIS fields, or wish to manually map fields.
    
1. Use the default mapping -- presumes the target file has either of the following sets of columns:

  CHGIS v5 standard fields:
  %s
  
  CHGIS v6 (Aug. 2016 draft) standard fields:
  %s
    

2. Use a manual mapping -- you will be prompted to indicate which column from the file should map to which output column.
''' % (str(default_target_fields_v5), str(default_target_fields_v6)))

accepted = False
mapping = input()

while accepted == False:
    # checks them against one another using comparison of sets (which are collections of unordered, unique items)
    if (mapping == '1'):
        # if the default target fields from CHGIS v5 are a subset of the target's fields, rename and use them while dropping the fields not in CHGIS v5 
        if all(item in set(list(target.columns)) for item in set(default_target_fields_v5)):
            # manually renaming one exception to the following pattern
            target.rename(columns={'src':'data_source'}, inplace=True)

            # manually dropping the 'seq' field
            del target['seq']
            
            # generating the target_mapping 
            target_mapping = OrderedDict([(key, 'tgaz_%s' % key) for key in target.columns]) 
            
            # renaming the target fields in-place to conform to output specifications
            target.rename(columns={key:value for key,value in target_mapping.items()}, inplace=True)
                        
            # dropping excess fields
            target = target[final_target_fields]
            target_fields = list(target.columns)
            accepted = True
      
        # if the default target fields from CHGIS v6 are a subset of the target's fields, rename and use them while dropping the fields not in CHGIS v6
        elif all(item in set(list(target.columns)) for item in set(default_target_fields_v6)):
            # renaming in preparation for "tgaz_" prefixing
            target.rename(columns={'geo_src':'data_source', 'type_simp':'type_ch', 'beg_yr':'beg', 'end_yr':'end' }, inplace=True)
            
            # generating target_mapping 
            target_mapping = OrderedDict([(key, 'tgaz_%s' % key) for key in target.columns])
            target.rename(columns={key:value for key,value in target_mapping.items()}, inplace=True)
                        
            # eliminating parent fields (since v6 data does not include parent information)
            for parent_item in ['tgaz_prnt_id', 'tgaz_prnt_sysid', 'tgaz_prnt_simp', 'tgaz_prnt_py']:
                final_target_fields.remove(parent_item) 
    
            # dropping other excess fields
            target = target[final_target_fields]
            target_fields = list(target.columns)
            accepted = True
        
        else: 
            print("The columns in the target .csv do not precisely match expectations. \n\n Proceeding with manual mapping.")
            for field, description in target_description.items():
                target_fields, target_mapping = field_mapper(field, description, target, target_fields, target_name, target_mapping)  
            target_fields = name_checker(['tgaz_nm_py', 'tgaz_nm_simp', 'tgaz_nm_trad'], target_fields, "tgaz", target)
            target = target[target_fields]
            accepted = True
    elif (mapping == '2'):
        print("Please specify fields from target .csv that will be included in output.\n")
        for field, description in target_description.items():
            target_fields, target_mapping = field_mapper(field, description, target, target_fields, target_name, target_mapping)  
        target_fields = name_checker(['tgaz_nm_py', 'tgaz_nm_simp', 'tgaz_nm_trad'], target_fields, "tgaz", target)
        target = target[target_fields]
        accepted = True
    else:
        print("\nNot a valid response.  Please try again:\n")
        mapping = input()


# In[11]:

# renaming fields in the incoming DataFrame to conform to specifications
print("Now we will specify fields from the incoming (match-making) data that will be included in the final spreadsheet.\n")
for field, description in incoming_description.items():
    incoming_fields, incoming_mapping = field_mapper(field, description, incoming, incoming_fields, incoming_name, incoming_mapping)    

incoming_fields = name_checker(['input_nm_py', 'input_nm_simp', 'input_nm_trad'], incoming_fields, "input", incoming)
incoming = incoming[incoming_fields]


# In[12]:

### titlecasing string values in pinyin fields to avoid spurious mismatches
title_caser(['tgaz_nm_py', 'tgaz_type_py'], target_fields, target)
title_caser(['input_nm_py', 'input_type_py'], incoming_fields, incoming)


# In[13]:

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
    if ((choice == '1') and ('input_nm_trad' in incoming_fields)):
        print("\nUsing name in complex/traditional Chinese characters 繁体字 as primary matching key.")
        accepted = True
        match_key = 'nm_trad'
        incoming_name_match_field = 'input_nm_trad'
        target_name_match_field = 'tgaz_nm_trad'
        df, name_mode = merge_chooser(target_name_match_field, incoming_name_match_field)
    elif ((choice == '2') and ('input_nm_simp' in incoming_fields)):
        print("\nUsing name in simplified Chinese characters 简体字 as primary matching key.")
        accepted = True
        match_key = 'nm_simp'
        incoming_name_match_field = 'input_nm_simp'
        target_name_match_field = 'tgaz_nm_simp'
        df, name_mode = merge_chooser(target_name_match_field, incoming_name_match_field)
    elif ((choice == '3') and ('input_nm_py' in incoming_fields)):
        print("\nUsing name in pinyin 拼音 as primary matching key.")
        accepted = True
        match_key = 'nm_py'
        incoming_name_match_field = 'input_nm_py'
        target_name_match_field = 'tgaz_nm_py'
        name_mode = 'strict'
        print('Fuzzy matching is not currently supported for pinyin names.  Proceeding with strict matching.')
        df = target.merge(incoming, how='outer', left_on=target_name_match_field, right_on=incoming_name_match_field, indicator=True)
        
    else:
        print("\nNot a valid response.  Please try again, entering a choice corresponding to a valid field:\n")
        choice = input()
        
output_fields = []            


# In[14]:

# removing rows that are only present in the CHGIS file
df = df[df['_merge'] != 'left_only']

# renaming merge indicators for legibility
df = df.replace(to_replace='both', value='found')
df = df.replace(to_replace='right_only', value='not_found')
df.rename(columns={'_merge':'match'}, inplace=True)


# In[15]:

### comparing spatial coordinates

spatial_coords = ['input_x_coord', 'input_y_coord', 'tgaz_x_coord', 'tgaz_y_coord']

# converting the given field's values to a numeric, or NaN, for possible rounding later
try: 
    for field in spatial_coords:
        #print("in the for loop")
        if (field in incoming_fields) or (field in target_fields):
            #print("converting %s" % field)
            df[field] = pd.to_numeric(df[field], errors='coerce')
    if ('input_x_coord' in incoming_fields) and ('input_y_coord' in incoming_fields):
        coord_mode, decimal_place = coordinate_matcher(['x', 'y'], df, output_fields)
    elif ('input_x_coord' in incoming_fields) and not ('input_y_coord' in incoming_fields):
        coord_mode, decimal_place = coordinate_matcher(['x'], df, output_fields)
    elif not ('input_x_coord' in incoming_fields) and ('input_y_coord' in incoming_fields):
        coord_mode, decimal_place = coordinate_matcher(['y'], df, output_fields)
    else:
        print("\nNo spatial coordinate fields available for matching.")
except KeyError:
    print("Spatial coordinates not properly entered. Skipping coordinate matching.")


# In[16]:

### handling administrative type matching
if ('input_type_ch' in incoming_fields) and ('input_type_py' in incoming_fields):
    print('''Administrative type information found in incoming data. Input the number for the field you want to match on:
        1. Pinyin ('Xian', 'Zhou', etc)
        2. Chinese ('县', '州', etc)
    ''')
    
    type_choice = input()
    accepted = False
    
    while accepted == False:
        if (type_choice) == '1':
            df['out_type_py_match'] = df['tgaz_type_py'] == df['input_type_py']
            accepted = True
            type_key = 'type_py'
            output_fields += ['out_type_py_match']
        elif type_choice == '2':
            df['out_type_ch_match'] = df['tgaz_type_ch'] == df['input_type_ch']
            accepted = True
            type_key = 'type_ch'
            output_fields += ['out_type_ch_match']
        else:
            print('Not a valid choice, please try again:')
            type_choice = input()
            
elif ('input_type_ch' in incoming_fields) and ('input_type_py' not in incoming_fields):
    print("The field 'input_type_py' could not be found; matching administrative type on field 'input_type_ch'")
    df['out_type_ch_match'] = df['tgaz_type_ch'] == df['input_type_ch']
    type_key = 'type_ch'
    output_fields += ['out_type_ch_match']
    
elif ('input_type_py' in incoming_fields) and ('input_type_ch' not in incoming_fields):
    print("The field 'input_type_ch' could not be found; matching administrative type on field 'input_type_py'")
    df['out_type_py_match'] = df['tgaz_type_py'] == df['input_type_py']
    type_key = 'type_py'
    output_fields += ['out_type_py_match']
    
else:
    print("Administrative type (e.g. 'Xian' or '县') could not be found in incoming data -- matching will not be attempted.")
    type_key = None 


# In[17]:

### handling year matching
if (not 'input_year_beg' in incoming_fields) or (not 'input_year_end' in incoming_fields):
    print("Incoming data lacks a beginning and/or ending year field; no date comparisons will be made.")
else:
    year_fields = ['input_year_beg', 'input_year_end', 'tgaz_beg', 'tgaz_end']
    
    # overlap field initialization
    df['out_year_overlap'] = ''
      
    # converting to type float64 (invalid years become 'NaN', and pandas.isnull(<Series_(column)>) returns True for those values
    for year_field in year_fields:
        df[year_field] = pd.to_numeric(df[year_field], errors='coerce')
    
    # in-row match testing
    df['out_beg_match'] = df['input_year_beg'] == df['tgaz_beg']
    df['out_end_match'] = df['input_year_end'] == df['tgaz_end']
    
    # testing for timespan relationships
    df['out_year_overlap'][((df['input_year_beg'] == (df['tgaz_end'] + 1)) | (df['input_year_end'] == (df['tgaz_beg'] - 1)))] = 'adjacent'
    df['out_year_overlap'][(df['input_year_beg'] <= df['tgaz_beg']) & (df['input_year_end'] >= df['tgaz_beg']) & (df['input_year_end'] < df['tgaz_end'])] = 'partial_incl_start_of_target'
    df['out_year_overlap'][(df['input_year_beg'] > df['tgaz_beg']) & (df['input_year_beg'] <= df['tgaz_end']) & (df['input_year_end'] >= df['tgaz_end'])] = 'partial_incl_end_of_target'
    df['out_year_overlap'][((df['input_year_beg'] >= df['tgaz_beg']) & (df['input_year_end'] < df['tgaz_end'])) | ((df['input_year_beg'] > df['tgaz_beg']) & (df['input_year_end'] <= df['tgaz_end']))] = 'incoming_nested_in_target'
    df['out_year_overlap'][((df['input_year_beg'] <= df['tgaz_beg']) & (df['input_year_end'] > df['tgaz_end']) | (df['input_year_beg'] < df['tgaz_beg']) & (df['input_year_end'] >= df['tgaz_end']))] = 'target_nested_in_incoming'
    df['out_year_overlap'][(df['input_year_beg'] == df['tgaz_beg']) & (df['input_year_end'] == df['tgaz_end'])] = 'perfect_match'
    df['out_year_overlap'][(df['input_year_beg'] == 0) | (df['input_year_end'] == 0) | (df['tgaz_beg'] == 0) | (df['tgaz_end'] == 0)] = 'CAUTION__ZEROES'
    df['out_year_overlap'][(df['input_year_beg'] > df['input_year_end']) | (df['tgaz_beg'] > df['tgaz_end'])] = 'ERROR__END_BEFORE_BEG'
    
    # designating items with non-numeric text values in at least one year field (which therefore break the overlap checker)
    df['out_year_overlap'][(df['match'] == 'found') & (pd.isnull(df['input_year_beg']) | pd.isnull(df['input_year_end']) | pd.isnull(df['tgaz_beg']) | pd.isnull(df['tgaz_end']))] = 'ERROR__NON_NUMERIC_YEAR_VALUE'
    
    # updating output fields
    output_fields += ['out_beg_match'] + ['out_end_match'] + ['out_year_overlap']


# In[18]:

# adding the 'match_strength' column, leveraging the fact that Python True and False evaluate to 1 and 0 respectively when passed to int()
df['out_content_match_strength'] = 0
output_fields += ['out_content_match_strength']

if ('input_x_coord' in incoming_fields):
    if coord_mode == "strict":
        df['out_content_match_strength'] += df['out_x_coord_match'].astype(int)
    else: 
        df['out_content_match_strength'] += df['fuzzy_out_x_coord_match'].astype(int)

if ('input_y_coord' in incoming_fields):
    if coord_mode == "strict":
        df['out_content_match_strength'] += df['out_y_coord_match'].astype(int)
    else: 
        df['out_content_match_strength'] += df['fuzzy_out_y_coord_match'].astype(int)
    
for field in ['out_beg_match', 'out_end_match', 'out_type_ch_match', 'out_type_py_match']:
    if field in list(df.columns):
        df['out_content_match_strength'] += df[field].astype(int)


# In[19]:

# sorting columns
ordered_fields = target_fields + incoming_fields + ['match'] + output_fields
fuzzy_ordered_fields = ['fuzzy_nm'] + ordered_fields

if name_mode == 'strict':
    df = df[ordered_fields]
else:
    df = df[fuzzy_ordered_fields]


# In[20]:

# replacing 'nan' with '' for improved legibility
df = df.replace('nan', '')


# In[21]:

# outputing results
print('\nData check is complete.  Please type a path (without extension) for your output files:\n')
output_path = input()
accepted = False

# validating output_path
#while accepted == False:
    # CHECK THAT FILENAMES DON'T ALREADY EXIST
    # CHECK THAT PATH IS VALID

print("Thank you. Saving results.")  

# writing the DataFrame to a .csv file at the specified output path while dropping the unlabeled index column that pandas DataFrames generate by default
df.to_csv("%s.csv" % output_path, index=False)

# creating the summary .info.txt file
summary_file = open("%s.info.txt" % output_path, "w")

# writing boilerplate 
summary_file.write("SUMMARY OF RESULTS\nGenerated at %s\n\n" % datetime.now().strftime("%H:%M, %m/%d/%Y"))

# writing compared & output filenames
summary_file.write("Incoming file: %s\n" % incoming_name)
summary_file.write("Target file: %s\n" % target_name)
summary_file.write("Output file: %s.csv\n\n" % os.path.basename(output_path))

# writing basic statistics
summary_file.write("Rows in incoming file: %s\n" % str(len(incoming.index)))
summary_file.write("Rows in target file: %s\n" % str(len(target.index)))
summary_file.write("Rows in output file: %s\n\n\n\n" % str(len(df.index)))

summary_file.write("FREQUENCY COUNTS\n")
summary_file.write("Counts given for all values; 'Name' is the field name in the output file, and 'dtype' simply indicates the type of the counts (i.e. integers)\n\n")
summary_file.write("Matches by name: \n")
summary_file.write(str(df['match'].value_counts()))
summary_file.write("\n\n")

if ('input_x_coord' in incoming_fields):
    if coord_mode == "strict":
        summary_file.write("X coordinate matches: \n")
        summary_file.write(str(df['out_x_coord_match'].value_counts()))
        summary_file.write("\n\n")
    else:
        summary_file.write("Fuzzy x coordinate matches: \n")
        summary_file.write(str(df['fuzzy_out_x_coord_match'].value_counts()))
        summary_file.write("\n\n")
if ('input_y_coord' in incoming_fields):
    if coord_mode == "strict":
        summary_file.write("Y coordinate matches: \n")
        summary_file.write(str(df['out_y_coord_match'].value_counts()))
        summary_file.write("\n\n")
    else:
        summary_file.write("Fuzzy y coordinate matches: \n")
        summary_file.write(str(df['fuzzy_out_y_coord_match'].value_counts()))
        summary_file.write("\n\n")
        
if 'out_beg_match' in list(df.columns):
    summary_file.write("Beginning year matches: \n")
    summary_file.write(str(df['out_beg_match'].value_counts()))
    summary_file.write("\n\n")
if 'out_end_match' in list(df.columns):
    summary_file.write("Ending year matches: \n")
    summary_file.write(str(df['out_end_match'].value_counts()))
    summary_file.write("\n\n")
if 'out_year_overlap' in list(df.columns):
    summary_file.write("Year overlaps: \n")
    summary_file.write(str(df['out_year_overlap'].value_counts()))
    summary_file.write("\n\n")
    
if 'out_type_ch_match' in list(df.columns):
    summary_file.write("Administrative type match (Chinese): \n")
    summary_file.write(str(df['out_type_ch_match'].value_counts()))
    summary_file.write("\n\n")
if 'out_type_py_match' in list(df.columns):
    summary_file.write("Administrative type match (pinyin): \n")
    summary_file.write(str(df['out_type_py_match'].value_counts()))
    summary_file.write("\n\n")

summary_file.write("Content match strengths: \n")
summary_file.write(str(df['out_content_match_strength'].value_counts()))
summary_file.write("\n\n\n\n")

# writing information about match

summary_file.write("BACKGROUND INFORMATION\n\n")
summary_file.write("The name match key was %s \n" % match_key)
summary_file.write("The name match mode was %s \n" % name_mode)
#summary_file.write("Report created at %s \n" % str(datetime.now)) 
type_key = None
if type_key:
    summary_file.write("The administrative type match key was %s\n" % type_key)
summary_file.write("The coordinate match mode was %s \n" % coord_mode)
if coord_mode == 'fuzzy':
    summary_file.write("Coordinates were rounded to %s decimal place(s)" % decimal_place)
summary_file.write("\n\n")
summary_file.write("The target file's fields were renamed as follows (not all fields are necessarily included in final output):\n") 
with summary_file as out:
    pprint(target_mapping, stream=out)
    
# reopening because pprint automatically closes file upon completion
summary_file = open("%s.info.txt" % output_path, "a")
summary_file.write("\n\n")
summary_file.write("The incoming file's fields were renamed as follows (not all fields are necessarily included in final output):\n")

with summary_file as out:
    pprint(incoming_mapping, stream=out)

summary_file = open("%s.info.txt" % output_path, "a")
summary_file.write("\n\n")
summary_file.write("The actual fields used in the output file are:\n")
with summary_file as out:
    pprint(list(df.columns), stream=out)

summary_file = open("%s.info.txt" % output_path, "a")
summary_file.write("\n\n\n")
summary_file.write("Report generated using geoname_match.py \nQuestions or concerns? Contact Stephen Ford (stephen.p.ford@gmail.com)")

# closing file
summary_file.close()

print("\nMatch results stored in %s.csv \n\nMatching info and summary of results stored in %s.info.txt \n\nNow exiting." % (os.path.basename(output_path), os.path.basename(output_path)))

