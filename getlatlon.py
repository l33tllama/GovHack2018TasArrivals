import urllib.request
import urllib.parse
import json
import csv
import pprint
from datetime import datetime, timedelta

def geocode_location(location):
	
	if len(location) > 0:
		location = urllib.parse.quote(location)
		print("Requesting location for " + location)	
		r = urllib.request.urlopen('https://maps.googleapis.com/maps/api/geocode/json?address=' + location + '&key=AIzaSyAs_NIPbbbBDRJs6g8CDUunqCNz3GK9Sqw')
		resp_str = r.read()
		#print(resp_str)
		resp_obj = json.loads(resp_str)
		#print(resp_obj['results']['geometry'])
		if len(resp_obj['results']) > 0:
			latlon = resp_obj['results'][0]['geometry']['location']
			pprint.pprint(latlon)
			return [latlon['lat'], latlon['lng']]
		else:
			return [-1, -1]
	else:
		return [-1, -1]
		

#lat, lon = geocode_location("Hobart")
#print(lat, lon)

def geocode_dataset():
	new_data = []
	locations = []
	locations_latlon = []
	# Get locations and replace location with location ID
	with open('arrivals.csv', 'rt') as arrivals_file:
		location_id = 0
		reader = csv.reader(arrivals_file, delimiter=',', quotechar='"')
		row_count = 0
		for row in reader:
			row_new = []
			if row_count > 0:
				for x in range(1, len(row)):
					if x == 21:
						index = 0
						found_location = False
						if row_count == 100:
							print(row[x])
						for location in locations:
							if location == row[x]:
								index = locations.index(location)
								#print("Index: " + str(index) + " location " + location)
								found_location = True
						if not found_location:
							#print("Not found location " + row[x] + ", adding.")
							locations.append(row[x])
							index = location_id
							location_id += 1

				row_new = row.copy()
				row_new[21] = str(index)
				new_data.append(row_new)
				if row_count == 100:
					pprint.pprint(row)
					print(index)
					print(locations)
			row_count += 1
		#print(locations[2])
	
		pprint.pprint(new_data[99])
		#pprint.pprint(reader[40])
	
	# check locations csv for existing locations and get lat lon from there
	locations_latlon = [0] * (len(locations) +1)
	with open('locations.csv', 'rt') as locations_file:
		reader = csv.reader(locations_file, delimiter=',', quotechar = '"')
		for row in reader:
			location_id = row[0]
			location_str = row[1]
			lat = row[2]
			lon = row[3]
			for location in locations:
				if location == location_str:
					location_index = locations.index(location)
					#print("Found existing lat lon: " + location + ": " + lat + ", " + lon)
					locations_latlon[location_index] = [lat, lon]

	for i in range(1, len(locations) +1):
		if locations_latlon[i-1] is 0:
			print("Need to look up lat/lon for " + locations[i-1])
			latlon = geocode_location(locations[i-1])
			locations_latlon[i-1] = [latlon[0], latlon[1]]

	with open('locations.csv', 'wt') as locations_file:
		writer = csv.writer(locations_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		row_id = 0
		for location in locations:
			lat = locations_latlon[row_id][0]
			lon = locations_latlon[row_id][1]
			writer.writerow([row_id, location, lat, lon])
			row_id += 1

	for row in new_data:
		location_id = int(row[21])
		latlon = locations_latlon[location_id]
		#print("Replaced " + str(location_id) + " with latlon " + str(latlon))
		row[21] = str(latlon)

	return new_data

def sort_by_year(data):
	new_data = {}
	row_id = 0
	for row in data:
		year = row[15]
		if not year in new_data:
			new_data[year] = []
		new_data[year].append(row)

		if row_id == 0:
			print(str(year))
		row_id += 1

	return new_data

def sort_year_dates(year, year_data):
	new_data = []
	try:
		year_int = int(year)
	except ValueError as e:
		return year_data
	print("Sorting year " + year)
	for row in year_data:
		date_str = row[17]
		dmy = []
		try:
			dmy = date_str.split(" ")
		except AttributeError as e:
			print("Error splitting " + str(date_str))
		day = dmy[0]
		month = ""
		year_val = ""
		date = datetime(year=int(year), month=1, day=1)
		if len(dmy) > 1:
			month = dmy[1]
		if len(dmy) > 2:
			year_val = dmy[2]
		try:
			date = datetime.strptime(year_val+" "+month+" "+day, "%Y %b %d")
		except ValueError as e:
			pass
			#print("Couldn't parse date: " + date_str)
		row[17] = date.strftime("%Y-%m-%d")
		new_data.append(row)
		#print(row[17])
	new_data.sort(key=lambda x: x[17])
	return new_data
	#pprint.pprint(new_data[0])
	#pprint.pprint(new_data[len(new_data)-1])


def make_cal_year(year, year_data):
	year_int = 0
	try:
		year_int = int(year)
	except ValueError as e:
		return

	cal_data = {}
	days_of_year = [0] * 367
	for row in year_data:
		timestamp = 0
		try:
			timestamp = datetime.strptime(row[17], "%Y-%m-%d").timestamp()
		except ValueError as e:
			pass
		try:
			datetimestamp = datetime.fromtimestamp(int(timestamp))
			doy = datetimestamp.timetuple().tm_yday
			try:
				days_of_year[doy] += 1
			except IndexError as e:
				print("index out of range: " + str(doy))
		except ValueError as e:
			print ("skipping " + timestamp)

	

	day_num = 0
	start_date = datetime(year=year_int, month=1, day=1)
	for day in days_of_year:
		date = start_date + timedelta(days=day_num)
		timestamp_str = str(date.timestamp())
		#print("Day " + str(day_num) + " count: " + str(day))
		cal_data[timestamp_str] = day
		day_num += 1

	return cal_data
	print(str(cal_data))



geocoded_data = geocode_dataset()
year_sorted_data = sort_by_year(geocoded_data)
#sort_year_dates('1833', year_sorted_data['1833'])

for key in sorted(year_sorted_data.keys()):

	entries = len(year_sorted_data[key])
	print("Year: " + key + " entries: " + str(entries))
	year_sorted_data[key] = sort_year_dates(key, year_sorted_data[key])
	
	with open('year_data/' + key + '.json', 'w') as outfile:
		json.dump(year_sorted_data[key], outfile)
	
	with open('year_data/' + key + '-cal.json', 'w') as outfile:
		cal_data = make_cal_year(key, year_sorted_data[key])
		json.dump(cal_data, outfile)	
	print("Saved")

make_cal_year('1855', year_sorted_data['1855'])

