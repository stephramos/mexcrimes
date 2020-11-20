import requests
import csv
import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon

FILE_DIR = os.path.join(os.path.dirname(__file__), './../data/cuadrantes.geojson')
CUAD = gpd.read_file(FILE_DIR)
CUAD["id"] = CUAD.index

def get_precinct(precincts, latitude, longitude):
    '''
    Obtains the number of precinct in Mexico City in which a point falls into.
    If the point is not in Mexico City, the function returns None.

    Input:
        -precincts: (geopandas dataframe) precincts information
        -latitude: (float) of a given point
        -longitude: (float) of a given point
    Returns:
        -id number of the precint or None if the point is not in Mexico City
    '''
    point = Point(longitude, latitude)
    
    for row in precincts.itertuples():
        if row.geometry.contains(point):
            return row.id

    return None

def geo_code(address):
    '''
    Computes the geo code (longitude and latitude) from a given address
    through the Google Geocoding API
    
    Input:
        -address (str): address to request the geocode

    Returns:
        -a tuple: ((lat, lon), precinct_id)
            *lat, lon: The geocode of address
            *precinct_id: the id of the precinct in which the point falls
        
        If the point is not in Mexico City returns None

    '''

    url = "https://maps.googleapis.com/maps/api/geocode/json?address={}".format(address)
    url = url + "&key=YOURKEY"

    r = requests.get(url)
    data = r.json()

    if data['status'] == 'OK':
        dic = r.json()['results'][0]['geometry']['location']
        lat = dic['lat']
        lon = dic['lng']

        precinct_id = get_precinct(CUAD, lat, lon)
        if precinct_id:
            return (lat,lon, precinct_id)
    
    return None
