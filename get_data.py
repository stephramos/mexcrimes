'''
File: Get_data.py
 
-Obtains the crime data and police districts(cuadrantes)
from datos.cdmx.gob.mx (Mexico City Open Data)

Creates 2 files:
    -geojson file of police districts
    -.sqlite3 database with 2 tables. One of crime data (clean) merged with 
     precinct data (table:crimes) and the second of police stations

Note: We only use crime data of 2018 and 2019
'''

import requests
import csv
import os
import data_cleaning
import geopandas as gpd
from shapely.geometry import shape, Polygon
import sqlite3
import shapely.wkb as swkb


url_cuad = 'https://datos.cdmx.gob.mx/api/v2/catalog/datasets/cua'+\
        'drantes/exports/geojson?rows=-1&timezone=UTC&pretty=false'

url_crimes = "https://datos.cdmx.gob.mx/api/v2/catalog/datasets/carpetas-de-"+\
        "investigacion-pgj-de-la-ciudad-de-mexico/exports/geojson?where=categoria_delito"+\
        "%20!%3D%20'HECHO%20NO%20DELICTIVO'%20AND%20ao_hechos%20%3D%202019%20OR%20ao_hechos"+\
        "%20%3D%202018&rows=-1&select=delito%2C%20ao_hechos%2C%20fecha_hechos%2C%20"+\
        "categoria_delito%2C%20colonia_hechos%2C%20alcaldia_hechos%2C%20longitud%2C%20latitud"+\
        "%2C%20geopoint&timezone=UTC&delimiter=%2C"

url_police_station = "https://datos.cdmx.gob.mx/api/v2/catalog/datasets/ubicacion-de-ministerios-publicos"+\
        "/exports/geojson?rows=-1&timezone=UTC&pretty=false"

def go():
    '''
    Gets crime data and police district data from Mexico City Portal API,
    merges the two dataframes and creates an .sqlite3 database.
    Also a geojson file is created with the police district data polygons.
    '''

    crimes = api_to_gpd(url_crimes)
    cuad = api_to_gpd(url_cuad)
    police = api_to_gpd(url_police_station)
    cuad["id"] = cuad.index
    data_cleaning.clean_crimes_data(crimes)
    crimes_merge = spacial_join(crimes, cuad)
    data_to_sql(crimes_merge, police, 'data/CrimesDB.sqlite3')
    data_to_csv(cuad, 'data/cuadrantes.geojson')


def api_to_gpd(url):
    '''
    Conects to API and returns data as geopandas dataframe
    Inputs:
        url: (str) url to connect to the API
    Outputs:
        data (geopandas dataframe)
    '''

    r = requests.get(url)
    r.raise_for_status()
    data = gpd.read_file(r.text)

    return data


def spacial_join(crime_data, cuad_data):
    '''
    Merges the crime_data with the precinct data according to their location.
    This function makes a spatial join on the polygon of the precinct and 
    location point of each crimes. 

    Input:
        -crime_data: (geopandas dataframe) crimes data
        -cuad_data: (geopandas dataframe) police precinct data
    Return:
        -merge (geopandas dataframe) merged data
    '''

    merge = gpd.sjoin(crime_data, cuad_data, how="inner", op="intersects")
    merge.index = range(len(merge))
    merge['geometry'] = merge['geometry'].astype('str')
    merge['geo_point_2d'] = merge['geo_point_2d'].astype('str')

    return merge


def data_to_sql(crime_data, police_stations, filename):
    '''
    Takes a geopandas dataframe and builds a sqlite 3 database with it.

    Input:
        -crime_data: geopandas dataframe (merged dataset)
        -police_stations: geopandas datafrane
        -filename: filename for the database
    '''

    police = police_stations.drop(columns=['geometry'])

    path = os.path.join(os.getcwd(), filename)
    conn = sqlite3.connect(path)
    crime_data.to_sql('crime', conn, if_exists='replace', index = False)
    police.to_sql('police_station', conn, if_exists='replace', index = False)
    conn.close()


def data_to_csv(cuad_data, filename):
    '''
    Takes a geopandas dataframe and writes it to geojson
    '''

    cuad_data.to_file(filename, driver='GeoJSON')


if __name__ == "__main__":
    go()
