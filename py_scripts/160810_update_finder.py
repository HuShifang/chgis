#! /usr/bin/python3
# simple regex matcher to find files modified in GISInfoTable_and_not_MainTable_20160810_A.ods

import pandas as import pd
from pandas import Series, DataFrame

df = pd.read_csv('/home/sf/chgis/input/GISInfoTable_and_not_MainTable_20160810_A.csv', low_memory=False)
# work with this later
