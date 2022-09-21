import urllib.request
import os
import numpy
import time
import pandas as pd
import multiprocessing
from numpy import asarray
from PIL import Image
from multiprocessing import Pool
    
class City:
    def __init__(self, name, lat, lon, date_length, level):
        self.name = name #name of the city
        self.row, self.col = self.get_tile(lat, lon, level) #row and column for the corresponding coordinates
        (self.lat_pos, self.lon_pos) = self.get_pos(self.row, self.col, lat, lon, level) #get position on image
        (self.lats, self.lons) = self.randomize_position(self.lat_pos, self.lon_pos, date_length) #randomize position of measured pixel
    
    #get tile from coordinates and zoom level
    def get_tile(self, lat, lon, level):
        row = int(((90 - lat) * (2 ** level)) // 288) #equation to find the row (from latitude)
        col = int(((180 + lon) * (2 ** level)) // 288) #equation to find the column (from longitude)
        return (row, col)
    
    #get city position within tile
    def get_pos(self, row, col, lat, lon, level):
        #find the minimum and maximum latitudes and longitudes that go on the same tile
        min_lat = -((row * 288) / (2 ** level)) + 90
        min_lon = ((col * 288) / (2 ** level)) - 180
        max_lat = (-(((row+1) * 288) / (2 ** level)) + 90) - 0.01
        max_lon = ((((col+1) * 288) / (2 ** level)) - 180) - 0.01
        
        #get the differences between minima and maxima for latitude and longitude
        lat_dif = max_lat - min_lat
        lon_dif = max_lon - min_lon
        
        #get approximate pixel point from the bottom/left
        lat_pos = (lat - min_lat) // 512
        lon_pos = (lon - min_lon) // 512
        
        return (lat_pos, lon_pos)
    
    #randomize latitude and longitude according to a gaussian distribution centered at exact pixel value
    def randomize_position(self, lat_pos, lon_pos, date_length):
        lats = []
        lons = []
        for _ in range(date_length):
            lat_rand = numpy.random.normal(0.0, 5.0) #generate random numbers (normal dist), center 0, standard dev 5
            lon_rand = numpy.random.normal(0.0, 5.0) #generate random numbers (normal dist), center 0, standard dev 5
            temp_lat = int(lat_pos) + int(lat_rand) #add random value to latitude
            temp_lon = int(lon_pos) + int(lon_rand) #add random value to longitude
            lats.append(temp_lat) #append to latitudes
            lons.append(temp_lon) #append to longitudes
        return (lats, lons)

#get data from images in the form of list of dictionaries with city name, date, and brightness value
def get_values(identifier, cities, i, url, dates):
    all_values = []
    date = dates[i]
    name = f'{i}-{identifier}.png' #name of local image file
    urllib.request.urlretrieve(url, name) #retrieve url
    im = Image.open(name, 'r') #open image
    im.convert('L') #convert image to black-white (8 bit)
    pix_val = asarray(im) #get image data as array
    for city in cities:
        lat = city.lats[i] #get latitude (row) position
        lon = city.lons[i] #get longitude (column) position
        value = pix_val[lat][lon] #get pixel brightness value
        temp_dict = {'name': city.name,
                    'date': date,
                    'value': value}
        all_values.append(temp_dict)
    os.remove(name) #remove file from computer
    return all_values

def main():
    
    #make a string of a number, and add 0 to the beginning if 1-digit
    def add_zero(number):
        number = str(number)
        if len(number) == 1:
            number = '0' + number
        return number
    
    #get list of urls from city information
    def get_urls(cities, dates, level, basic):
        urls = dict()
        row_list = []
        col_list = []
        for city in cities:
            row_list.append(city.row)
            col_list.append(city.col)
        row_list = list(set(row_list))
        col_list = list(set(col_list))
        for row in row_list:
            for col in col_list:
                urls[f'{row}-{col}'] = []
                for date in dates:
                    urls[f'{row}-{col}'].append(f'{basic}{date}/500m/{level}/{row}/{col}.png')
        return urls
    
    #get dictionary of unique row-column combinations for each city, along with corresponding cities
    def get_cities(citylist):
        identifiers = dict()
        for city in citylist:
            if f'{city.row}-{city.col}' not in identifiers:
                identifiers[f'{city.row}-{city.col}'] = [city]
            else:
                identifiers[f'{city.row}-{city.col}'].append(city)
        return identifiers
    
    #transpose a matrix
    def transpose(matrix):
        num_rows = len(matrix[0])
        num_columns = len(matrix)
        Final = [[0]*num_columns for x in range(num_rows)]
        for x in range(num_rows):
            for i in range(num_columns):
                Final[x][i] = matrix[i][x]
        return Final
    
    #get a vector from a matrix
    def squish(collection):
        final = []
        for row in collection:
            final += row
        return final
    
    #define zoom level, basic url, and get list of dates
    basic = 'https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/VIIRS_SNPP_DayNightBand_At_Sensor_Radiance/default/'
    day_dict = {
    '01': 31,
    '02': 28,
    '03': 31,
    '04': 30,
    '05': 31,
    '06': 30,
    '07': 31,
    '08': 31,
    '09': 30,
    '10': 31,
    '11': 30,
    '12': 31,
    }
    dates = []
    for month in [add_zero(x+1) for x in range(12)]:
        days = day_dict[month]
        for day in [add_zero(x+1) for x in range(days)]:
            dates.append(f'2021-{month}-{day}')
    date_length = len(dates)
    
    level = 7
    
    #make dictionary of information for cities
    info_list = [
    {'name': 'Bata', 'lat': 1.87, 'lon': 9.77},
    {'name': 'Malabo', 'lat': 3.75, 'lon': 8.77},
    {'name': 'Ebebiyín', 'lat': 2.15, 'lon': 11.32},
    {'name': 'Aconibe', 'lat': 1.30, 'lon': 10.93},
    {'name': 'Añisoc', 'lat': 1.85, 'lon': 10.77},
    {'name': 'Luba', 'lat': 3.45, 'lon': 8.55},
    {'name': 'Evinayong', 'lat': 1.45, 'lon': 10.57},
    {'name': 'Mongomo', 'lat': 1.65, 'lon': 11.32},
    {'name': 'Mengomeyén', 'lat': 1.69, 'lon': 11.03},
    {'name': 'Micomeseng', 'lat': 2.13, 'lon': 10.62},
    ]
    
    #make list of city objects
    cities = []
    for info in info_list:
        temp_city = City(info['name'], info['lat'], info['lon'], date_length, level)
        cities.append(temp_city)
    
    #collect urls and city identifiers
    all_urls = get_urls(cities, dates, level, basic)
    identifiers = get_cities(cities)
    
    #organize data to put into starmap
    input_data = []
    for identifier in identifiers:
        for i, url in enumerate(all_urls[identifier]):
            input_data.append([identifier, cities, i, url, dates])
    
    #all_values = [get_values(input[0], input[1], input[3], input[4], input[5]) for input in input_data]
    with Pool() as pool:
        all_values = pool.starmap(get_values, input_data) #get data
    
    all_values = squish(all_values) #turn matrix into vector
    all_values = [[item['name'], item['date'], item['value']] for item in all_values] #put values in list
    all_values = transpose(all_values) #transpose values
    df = pd.DataFrame(all_values, ['Name', 'Date', 'Value']) #make pandas dataframe with luminosity data
    df = df.transpose() #transpose dataframe
    df.to_csv('data.csv', encoding='utf8') #write to csv

if __name__ == '__main__':
    main()