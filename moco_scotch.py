#munging json scotch data from moco's website
import json
import pandas as pd
import difflib

with open('moco_scotch.json') as f:
	data = json.load(f)

moco = pd.DataFrame(data['d'])
moco_cols_to_keep = ['description','price','size','saleprice']
moco = moco[moco_cols_to_keep]

#replace moco price with sales price if sale price populated
moco.ix[moco['saleprice']!='N/A','price'] = moco.ix[moco['saleprice']!='N/A','saleprice'] 

#dropping and renaming columns to match up to total wine table
moco = moco.drop('saleprice',axis=1)
cols_to_rename = {
		'description': 'moco_name',
		'size': 'volume',
		'price': 'moco_price'
}
moco = moco.rename(columns=cols_to_rename)

#load in total wine scotch data
tw = pd.read_csv('totalwine_scotch.csv')
tw_cols_to_keep = ['name','volume','price']
tw = tw[tw_cols_to_keep]	
tw = tw.dropna()

cols_to_rename = {
		'price': 'tw_price',
		'name': 'tw_name'
}

tw = tw.rename(columns=cols_to_rename)

#add column of names to moco table that is 'closest' to names in total wine table
moco['moco_name']=moco['moco_name'].str.title()
moco['name_list'] = moco['moco_name'].map(lambda x: difflib.get_close_matches(x, tw['tw_name']))

moco['tw_name'] = ''
for i in range(len(moco.index)):
	if len(moco['name_list'][i])==0:
		moco['tw_name'][i] = ''
	else:
		moco['tw_name'][i] = moco['name_list'][i][0]

moco = moco.drop('name_list',axis=1)

#adjust capitalization in volume column for both data sets
tw['volume'] = tw['volume'].str.title()
moco['volume'] = moco['volume'].str.title()

#strip $ from total wine prices
tw['tw_price'] = tw['tw_price'].map(lambda x: x.lstrip('$')) 
tw['tw_price'] = tw['tw_price'].str.replace(',','')

#merge two tables
merged = tw.merge(moco, how='inner', on=['tw_name', 'volume'])

cols_in_order = ['tw_name','moco_name','volume','tw_price','moco_price']
merged = merged[cols_in_order]

#change price types to float
merged['tw_price'] = merged['tw_price'].astype('float')
merged['moco_price'] = merged['moco_price'].astype('float')

merged['abs_change'] = merged['tw_price']-merged['moco_price']
merged['per_change'] = merged['abs_change']/merged['tw_price']

merged.to_csv('price_compare.csv')
