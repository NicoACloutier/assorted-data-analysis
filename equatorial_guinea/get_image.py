def main():
    import urllib.request
    import os
    import numpy
    import time
    
    class City:
        def __init__(self, name, lat, lon, level, dates):
            self.name = name #name of the city
            self.level = level #zoom level, maximum 7
            self.row, self.col = self.get_tile(lat, lon, level) #row and column for the corresponding coordinates
            self.dates = dates #list of dates
            self.urls = self.get_urls() #urls for the inputted information
            self.pos = self.get_pos(self.row, self.col, lat, lon, level) #get position on image
            
        
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
        
        #get list of urls from city information
        def get_urls(self):
            urls = []
            for date in self.dates:
                urls.append(f'https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/VIIRS_SNPP_DayNightBand_At_Sensor_Radiance/default/{date}/500m/{self.level}/{self.row}/{self.col}.png')
            return urls
        
        #randomize latitude and longitude according to a gaussian distribution centered at exact pixel value
        def randomize_position(lat_pos, lon_pos, urls):
            lats = []
            lons = []
            for url in urls:
                (lat_rand, lon_rand) = numpy.random.normal(0.0, 3.0, 2) #generate random numbers (normal dist)
                temp_lat = lat_pos + int(lat_rand) #add random value to latitude
                temp_lon = lon_pos + int(lon_rand) #add random value to longitude
                lats.append(temp_lat) #append to latitudes
                lons.append(temp_lon) #append to longitudes
            return (lats, lons)
    
    #make a string of a number, and add 0 to the beginning if 1-digit
    def add_zero(number):
        number = str(number)
        if len(number) == 1:
            number = '0' + number
        return number
    
    #define zoom level and get list of dates
    level = 7
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
    
    #make dictionary of information for cities
    info_list = [
    {'name': 'Bata', 'lat': 1.87, 'lon': 9.77, 'level': level, 'dates': dates},
    {'name': 'Malabo', 'lat': 3.75, 'lon': 8.77, 'level': level, 'dates': dates},
    {'name': 'Ebebiyín', 'lat': 2.15, 'lon': 11.32, 'level': level, 'dates': dates},
    {'name': 'Aconibe', 'lat': 1.30, 'lon': 10.93, 'level': level, 'dates': dates},
    {'name': 'Añisoc', 'lat': 1.85, 'lon': 10.77, 'level': level, 'dates': dates},
    {'name': 'Luba', 'lat': 3.45, 'lon': 8.55, 'level': level, 'dates': dates},
    {'name': 'Evinayong', 'lat': 1.45, 'lon': 10.57, 'level': level, 'dates': dates},
    {'name': 'Mongomo', 'lat': 1.65, 'lon': 11.32, 'level': level, 'dates': dates},
    {'name': 'Mengomeyén', 'lat': 1.69, 'lon': 11.03, 'level': level, 'dates': dates},
    {'name': 'Micomeseng', 'lat': 2.13, 'lon': 10.62, 'level': level, 'dates': dates},
    ]
    
    #make list of city objects
    cities = []
    for info in info_list:
        temp_city = City(info['name'], info['lat'], 
                         info['lon'], info['level'], 
                         info['dates'])
        cities.append(temp_city)
    
    start = time.time()
    for city in cities:
        for url in city.urls:
            urllib.request.urlretrieve(url, "image.png")
    end = time.time()
    elapsed = end - start
    print(f'{elapsed:.3f}')

if __name__ == '__main__':
    main()