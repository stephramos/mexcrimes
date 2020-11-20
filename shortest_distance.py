'''
File name: shortest_distance.py

This module finds the nearest police station from the given address.

Calls --> CrimesDB.sqlite3 database
'''
from math import radians, cos, sin, asin, sqrt
import sqlite3
import os

DATABASE_FILENAME = os.path.join(os.getcwd(), 'data/CrimesDB.sqlite3')

def get_police_station(latitude, longitude):
    '''
    Finds the closest police station from a given point.

    Input:
        -latitude (float) latitude from given address
        -longitude (float) longitude from given address
    Output:
        -data_row (tuple): latitude of the police station,
                         longitude of police station,
                         distance from address
    '''

    connection = sqlite3.connect(DATABASE_FILENAME)
    c = connection.cursor()
    connection.create_function('distance', 4, distance)

    sel = "latitud, longitud, min(distance(?, ?, latitud, longitud)) AS kilometers"
    frm = "police_station"
    query = "SELECT {} FROM {}".format(sel, frm)
    args = (latitude, longitude)

    data_row = c.execute(query, args).fetchone()

    connection.close()

    return data_row


def distance(lat1, long1, lat2, long2):
    '''
    Calculates the circle distance between two points
    on the earth on kilometers

    Inputs:
        -lat1, long1 (floats) latitude and longitude from point 1
        -lat2, long2 (floats) latitude and longitude from point 2
    Returns:
        -distance_km: (float) distances in kilometers from point 1 to point2
    '''

    long1, lat1, long2, lat2 = map(radians, [long1, lat1, long2, lat2])

    dlong = long2 - long1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlong / 2)**2
    c = 2 * asin(sqrt(a))

    distance_km = 6367 * c

    return distance_km
