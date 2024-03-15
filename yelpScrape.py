import csv 

import requests
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup
#from webtools import webanon												My personal library that randomizes user agents for easier scraping

import string
import time 
import pandas as pd


def fileWriter(phone_numbers, store_hours, file_path):

	df = pd.read_csv(file_path)

	df['Hours'] = pd.Series(store_hours)
	df['Phone Numbers'] = pd.Series(phone_numbers)

	df.to_csv(file_path, index=False)






def fileOpener(file_path):

	restaurant_names = []
	addresses = []


	with open(file_path, newline='') as csvfile:
		restaurants = csv.reader(csvfile, delimiter=' ', quotechar=' ')
		for row in restaurants:
			format_row = ' '.join(row)
		
			splitrow = list(format_row.split(','))
		#	print(splitrow)
			if '(3' not in splitrow[0] and splitrow[0] != 'AUSTIN' and (splitrow[0].isupper() == False or splitrow[0] == 'TXB62') and splitrow[0] != 'Restaurant Name':	
				if splitrow[0][0] == '\"':
					restaurant_names.append(splitrow[0][1:])
				else:
					restaurant_names.append(splitrow[0])
#				print(restaurant_names)

			for s_row in splitrow:
				if s_row.isupper() == True and s_row != 'AUSTIN' and 'TX' not in s_row and s_row[0] == '\"':
					addresses.append(s_row[1:] + " AUSTIN TX")

		return restaurant_names, addresses


def yelpScrape(url, names, addresses, phone_numbers, store_hours):

	time.sleep(10)

	yelp_links = []

#	print(url)
#	web = webanon()							 			My personal library that randomizes user agents for easier scraping
#	user_agent = web.agent()
#	headers = {'User-Agent': user_agent}
	res = requests.get(url)#, headers=headers)
	yelp_scrape = BeautifulSoup(res.text, "lxml")


#	print(yelp_scrape)
	
	for div in yelp_scrape.find_all('a', href=True):
		for n_name in str(names).split():							
			if n_name in str(div) and "/search" not in str(div):
				yelp_links.append(div['href'])
#				print(div['href'])

	parsed_links = []

	for links in yelp_links:
		if names in links:
			parsed_links.append(links)
		else:
			newer_name = names.replace('+', '-')
			newer_name = names.lower()
		#	print(newer_name, links)
			if newer_name in links:
				parsed_links.append(links)


	res.close()
#	print(parsed_links)
	time.sleep(5)


#	user_agent = web.agent()
#	headers = {'User-Agent': user_agent}
	res = requests.get(url)#, headers=headers)
	res = requests.get('https://www.yelp.com/' + parsed_links[0])#, headers=headers)
	yelp_info = BeautifulSoup(res.text, "lxml")


	phone_number = yelp_info.find_all('div', class_="css-s81j3n")
#	print(phone_number)
	phone_number = str(phone_number)

	hours = yelp_info.find_all('table', class_="hours-table__09f24__KR8wh css-n604h6")
#	print(hours)
	hours = str(hours)

	phone_number = phone_number.split()
	hours = hours.split('>')


#	print(hours)

	for phone_n in phone_number:
		if '(' in phone_n:
			entrynum = phone_number.index(phone_n)
			phoneNumber = phone_number[entrynum:entrynum + 2]
		#	print("Phone Number: " + str(phoneNumber))
			phone_numbers.append(phoneNumber[0][-5:-1] + ')' + phoneNumber[-1][0:8])
			#print(p_n)


	#Every entry in hours is sandwiched between a '>' and '</p>' tag

	dateTime = []
	storeHours = []

	for hour in hours:
		if '</p' in hour:
			dateTime.append(hour)

	for d_t in dateTime:
		d_t = d_t[0:-3]
		storeHours.append(d_t)

	store_hours.append(storeHours)
	
	#print(store_hours)

#	print(names, addresses, phone_numbers[-1], store_hours[-1])

	res.close()




def stringParser(restaurant_names):

#Remove any strings before a '-' or after a '#' before searching (These seem to inhibit accurate search results)

	name_number_splitter = []
	name_dash_splitter = []
	name_both_splitter = []
	name_LLC_splitter = []

	clean_name = []

	for r_names in restaurant_names:
	#	print(r_names)
		if '#' in r_names and ' - ' in r_names:
			name_both_splitter.append(r_names)
		elif '#' in r_names:
			name_number_splitter.append(r_names)
		elif ' - ' in r_names:
			name_dash_splitter.append(r_names)
		elif 'LLC' in r_names:
			name_LLC_splitter.append(r_names)
			
	for nns in name_number_splitter:
		nns = nns.split(' #')
	#	nns = nns[0].split('No.')
		clean_name.append(nns[0])

	for nds in name_dash_splitter:
		nds = nds.split(' - ')
		clean_name.append(nds[1])

	for nbs in name_both_splitter:
		nbs = nbs.split(' #')
	#	nbs = nbs[0].split(' No. ')
		nbs = nbs[0].split(' - ')
		clean_name.append(nbs[1])

	for nlc in name_LLC_splitter:
		nlc = nlc.split('LLC')
		clean_name.append(nlc[0])

	for c_n in clean_name:
		for restaurant_name in restaurant_names:
			if c_n in restaurant_name:
				original_index = restaurant_names.index(restaurant_name)
				restaurant_names[original_index] = c_n
	
if __name__ == "__main__":


	# Build a simple script that can read in a csv of restaurants and their addresses then find that restaurant on yelp, scrape the url and restaurant phone number and hours then add them to the csv. 

	file_path = "C:/Users/inves/Desktop/Python Projects/names - names.csv"	#MAKE SURE FILE PATH IS CORRECT BEFORE RUNNING

	restaurant_names, addresses = fileOpener(file_path)
	
	

	phone_numbers = []
	store_hours = []
	
	stringParser(restaurant_names)

#	print(addresses)

	url_restaurant_names = []	
	url_addresses = []

#	print(restaurant_names) 

	for r_n in restaurant_names:
		r_n = r_n.replace("&", "and")
		r_n = r_n.replace(",", "")
		r_n = r_n.replace("\'", "")
		r_n = r_n.replace(' ','+')

		if r_n[-1] == '+':
			url_restaurant_names.append(r_n[:-1])
		else:
			url_restaurant_names.append(r_n)

	for addr in addresses:
		addr = addr.replace(' ', '+')
		url_addresses.append(addr)

#	print(restaurant_names)
#	i = 22

#	url = "https://www.yelp.com/search?find_desc={}+&find_loc={}".format(url_restaurant_names[i], url_addresses[i])
#	yelpScrape(url, url_restaurant_names[i], url_addresses[i], phone_numbers, store_hours)

#	print(restaurant_names[i], addresses[i], phone_numbers, store_hours)

	
	for i in range(len(addresses)):
#		break
		try:
			url = "https://www.yelp.com/search?find_desc={}+&find_loc={}".format(url_restaurant_names[i], url_addresses[i])
			yelpScrape(url, url_restaurant_names[i], url_addresses[i], phone_numbers, store_hours)
			print(restaurant_names[i], addresses[i], phone_numbers[i], store_hours[i])
		except Exception as e:
			try:
				print("ERROR ON: " + str(restaurant_names[i]) + " BECAUSE OF {}".format(e))
				time.sleep(60)
				yelpScrape(url, url_restaurant_names[i], url_addresses[i], phone_numbers, store_hours)
				continue
			except IndexError:
				phone_numbers.append(None)
				store_hours.append(None)


	fileWriter(phone_numbers, store_hours, file_path)

  	# NONEXISTANT ENTRIES: RBG Kitchen, Timewise Food Store, ABIA-Heart of Austin (Main Kitchen), Man Pasand Supermarket-Kitchen, Meat and Seafood, Oak Meadows Elementary
	#Foodspot 1 Grocery Inc, Sedona Trace Health and Wellness, TXB62

#	
