'''
CAPP 30122 W'20: Final Poject

This module performs queries in the crimes database and calls
the visualizations file to produce maps and plots

'''

import sqlite3
import os
import pandas as pd
import geopandas as gpd
import viz
import shortest_distance


DATABASE_FILENAME = os.path.join(os.getcwd(), 'data/CrimesDB.sqlite3')
CSV_FILENAME = os.path.join(os.getcwd(), "data/cuadrantes.geojson")


def get_viz(dic):
    '''
    Produces all the visualizations that are shown through django.
    Inputs:
        dic (dictionary): contains the data introduced by the user
    Outputs:
        tuple of follium map objects. This funcion also exports two barplots
        to the visualizations folder.
	'''

    lat, lon, prec = dic["address"]

    cuadrantes = gpd.read_file(CSV_FILENAME)
    crime_map = filter_data(dic, "id")
    crime_map = add_zero_precincts(crime_map, cuadrantes)
    viz.map(crime_map, cuadrantes, "viz/map_all.html", lat, lon)

    map_cuad = filter_data(dic, None)
    if map_cuad.empty:
        return False

    cuad = cuadrantes[cuadrantes.id == prec]
    pol_station = shortest_distance.get_police_station(lat, lon)
    viz.map_cuad(map_cuad, cuad, "viz/map_cuad.html", lat, lon, pol_station)

    crime_bar_week = filter_data(dic, "weekday")
    crime_bar_week = add_days(crime_bar_week)
    viz.barplot(crime_bar_week, 'weekday', 'viz/bar_week.png', dic)

    crime_bar_hour = filter_data(dic, "hour")
    crime_bar_hour = add_hours(crime_bar_hour)
    viz.barplot(crime_bar_hour, 'hour', 'viz/bar_day.png', dic)

    return True


def filter_data(dic, group_var):
    '''
    Filters and groups crime data necessary to produce visualizations.
    Inputs:
        dic (dictionary): contains the data introduced by the user.
        group_var (str): variable to group by (none, id, weekday, hour)
    Outputs:
        pandas dataframe
	'''

    connection = sqlite3.connect(DATABASE_FILENAME)
    c = connection.cursor()

    args, query = get_query(dic, group_var)
    data_r = c.execute(query, args).fetchall()

    if group_var:
        cols = [group_var, "crimes"]
    else:
        cols = ["latitud", "longitud", "delito"]

    connection.close()

    df = pd.DataFrame(data_r, columns=cols)

    return df


def get_query(dic, group_var):
    '''
    Obtain sql query and arguments.
    Inputs:
        dic (dictionary): contains the data introduced by the user.
        group_var (str): variable to group by (none, id, weekday, hour)
    Output:
        tuple of query and arguments
	'''

    args = ()
    where = []

    if group_var:
        select = "{}, count(*) FROM crime".format(group_var)
    else:
        select = "latitud, longitud, delito FROM crime".format(group_var)

    if group_var != "weekday":
        where.append("weekday = ?")
        args += (dic["day"],)

    if group_var == "id" or group_var is None:
        where.append("hour >= ?")
        where.append("hour <= ?")
        args += (dic["hour"][0], dic["hour"][1])

    if group_var != "id":
        where.append("id = ?")
        args += (dic["address"][2],)

    args_type, where_type = get_query_crimetype(dic["crime_type"])
    args += args_type
    where.append(where_type)

    where_query = ' AND '.join(where)

    if group_var:
        query = "SELECT {} WHERE {} GROUP BY {}".format(select, where_query, group_var)
    else:
        query = "SELECT {} WHERE {}".format(select, where_query)

    return (args, query)


def get_query_crimetype(crime_type):
    '''
    Produces the part of the query related to the type of crime introduced
    by the user
    Input:
        crime_type: list of crime types to be considered
    Output:
        tuple containing arguments and query
	'''

    args = ()
    dic_cat = {1: "walking", 2:"public transit", 3:"personal vehicle"}
    q_marks = '?' + ', ?'*(len(crime_type))

    if 1 in crime_type or 2 in crime_type:
        args += ("rape",)
        q_marks += ', ?'

    args += ("homicide",)

    for val in crime_type:
        args += (dic_cat[val],)

    where = "tipo in ({})".format(q_marks)

    return (args, where)


def add_zero_precincts(crime_data, precinct_data):
    '''
    adds missing precincts to the data with value 0
    '''

    crime = pd.merge(crime_data, precinct_data["id"], on="id", how="right")
    crime = crime.fillna(0)

    return crime


def add_days(crime_data):
    '''
    adds missing days to the data with value 0
    '''

    week_days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday',
                 'Friday', 'Saturday']
    days = pd.Series(week_days, name="weekday")
    crime = pd.merge(crime_data, days, on="weekday", how="right")
    crime = crime.fillna(0)

    return crime


def add_hours(crime_data):
    '''
    adds missing hours to the data with value 0
    '''

    hours = pd.Series(list(range(24)), name="hour")
    crime = pd.merge(crime_data, hours, on="hour", how="right")
    crime = crime.fillna(0)
    crime = crime.sort_values(by=['hour'])

    return crime
