#scraping whiskey data from total wine's site
import requests
import pyquery as pq 
import pandas as pd


url = 'http://www.totalwine.com/eng/categories/spirits/scotch%7Cscotch!viewPerPage/351'
cookies={'TOTALWINE_COOKIEPREFERREDLOCATION':'PICKUP|MD|17825'}
r = requests.get(url, cookies=cookies)

#parse html
parsed = pq.PyQuery(r.text) #or r.content?

#need to create table with product name and price from product summary page/list
#is this pulling the correct prices? not matching what I am seeing on online. maybe looking at two different stores?
product_list = parsed('.product')
print('constructing price data')
price_data = [{
	'name': product_list.eq(i).find('h2').text(),
	'volume':  product_list.eq(i).find('p').eq(0).text(),
	'price': product_list.eq(i).find('.productPrice').text(),
	'customer_rating': product_list.eq(i).find('.rating-star').find('img').attr['src'].split('-')[1].split('.')[0].replace('_','.'),
	'customer_rating_no': product_list.eq(i).find('.rating-star').find('a').text().split(' ')[2],
	'commercial_rating': product_list.eq(i).find('#rating-box').find('#points').text(),
	'commercial_rater': product_list.eq(i).find('#rating-box').find('#target').text()
} for i in range(len(product_list))]

#grab all of the a tags with hrefs to whisky detail pages
a_tags = parsed('.moreBtn')

#grab hrefs from all the a tags
links = [tag.attrib['href'] for tag in a_tags]
print('drilling into detail product pages')
counter = 0 
whiskey_list = []
for link in links:
	counter += 1
	print(counter)

	prod = requests.get(link)
	prod_parsed = pq.PyQuery(prod.text) #or prod.content?

	name = prod_parsed('#additionalDetails').find('h1').text()
	short_desc = prod_parsed('#profile-box').text() 

	#long_desc = prod_parsed('#review-main-box').text()	

	volume = prod_parsed('#additionalDetails').find('div.format').text()

	item = {
		'name': name,
		'volume': volume,
		'short_desc': short_desc,
		#'long_desc': long_desc,
	}

	whiskey_list.append(item)

df_prices = pd.DataFrame(price_data)
df_whiskey = pd.DataFrame(whiskey_list)
merged = df_whiskey.merge(df_prices, how='left', on=['name','volume'])

merged.ix[merged['customer_rating_no']=='Review',['customer_rating','customer_rating_no']] = ''

merged.to_csv('totalwine_scotch.csv')
