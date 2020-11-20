'''
CAPP 30122 W'20: Final Poject

This module produces all visualizations
'''

import folium
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns

matplotlib.use('Agg')

def map(crime_data, precinct_data, name_map, latitude=None, longitude=None):
    '''
    Creates choropleth map html
    Input:
        crime_data (dataframe)
        precinct_data (dataframe)
        name map
	'''

    m = folium.Map(location=[19.432608, -99.133209], zoom_start=11)

    if latitude and longitude:
        popup = 'Your Address'
        folium.Marker(location=[latitude, longitude],
                      popup=popup,
                      icon=folium.Icon(color='red', icon='home'),
                      tooltip='Click me!').add_to(m)

    folium.Choropleth(
        geo_data=precinct_data,
        name='choropleth',
        data=crime_data,
        columns=['id', 'crimes'],
        key_on='properties.id',
        fill_color='BuPu',
        fill_opacity=1,
        line_opacity=1,
        legend_name='Choropleth of Crimes per Precinct : 2018-2019',
        highlight=True).add_to(m)

    folium.TileLayer('openstreetmap').add_to(m)
    folium.TileLayer('cartodbpositron').add_to(m)
    folium.TileLayer('cartodbdark_matter').add_to(m)
    folium.LayerControl().add_to(m)

    m.save(name_map)


def barplot(crimes, group_var, name_plot, dic):
    '''
    Creates a barplot showig number of crimes by day and hour.
    Inputs:
        crimes (data frame): filtered crime data frame
        group_var (str): variable to group by (weekday or hour)
        name_plot (str): name of the figure
        dic (dictionary): input from the user
    '''

    sns.set(style="ticks")

    if group_var == 'weekday':
        d = {'Sunday': 0, 'Monday':1, 'Tuesday':2, 'Wednesday':3, 'Thursday':4,
             'Friday':5, 'Saturday':6}
        clrs = ['steelblue']*7
        day = dic['day']
        clrs[d[day]] = 'red'
        order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday',
                 'Friday', 'Saturday']
    else:
        clrs = ['red' if (x >= dic['hour'][0] and x <= dic['hour'][1]) else
                'steelblue' for x in crimes.hour]
        order = None

    sns.set(font_scale=1.4) 
    fig, ax = plt.subplots(figsize=(10, 10))

    sns.barplot(x=group_var,
                y='crimes',
                data=crimes,
                order=order,
                palette=clrs)

    if group_var == 'weekday':
        title = 'Crime by day of the week (all hours)'
    else:
        title = 'Crime by time of the day' + ' ({})'.format(dic['day'])
    plt.title(title, fontsize=20)

    plt.savefig(name_plot)
    plt.close()


def map_cuad(crimes, cuadrante, name_plot, latitude, longitude, pol_station):
    '''
    Creates map of a given precinct with markers of crimes ocurred
    in that area.
    Inputs:
        crimes: filtered data frame
        cuadrante(int): id of the oprecinct to map
        name_plot(str): name of the map
        latitude(int): introduced bu the user
        longitude(int): introduced by the user
        pol_station(tuple): (latitude, longitude, distance) of nearest
        police station
    '''

    m = folium.Map(location=[latitude, longitude],
                   zoom_start=16,
                   color='RGBA')
    folium.GeoJson(cuadrante).add_to(m)

    for crime in crimes.iterrows():
        popup = crime[1].delito
        folium.Marker(location=[crime[1].latitud, crime[1].longitud],
                      popup=popup,
                      icon=folium.Icon(color='blue', icon='info-sign'),
                      tooltip='Reported Crime!'
                      ).add_to(m)

    folium.Marker(location=[latitude, longitude],
	              popup='To find nearest police station folllow the green line',
                  icon=folium.Icon(color='red', icon='home'),
                  tooltip='Your Address'
                  ).add_to(m)
    
    folium.Marker(location=[pol_station[0], pol_station[1]],
                  popup='Nearest Police station:'+
                        ' {:.2f} kilometers'.format(pol_station[2]),
                  icon=folium.Icon(color='green', icon='cloud'),
                  tooltip='Police station'
                  ).add_to(m)

    points = [[latitude, longitude],[pol_station[0], pol_station[1]]]
    folium.PolyLine(points,color="green", weight=2.5, opacity=1).add_to(m)

    legend_html = """
        <div style='position: fixed; 
        bottom: 10px; left: 10px; width: 130px; height: 100px; 
        border:2px solid black; z-index:9999; font-size:12px;
        background-color:white;
        '>&nbsp; Legend <br>
        &nbsp; Your Address   &nbsp; <i class='fa fa-map-marker fa-2x'
                      style='color:red'></i><br>
        &nbsp; Police Station  &nbsp; <i class='fa fa-map-marker fa-2x'
                      style='color:green'></i><br>
        &nbsp; Reported Crime &nbsp; <i class='fa fa-map-marker fa-2x'
                      style='color:DeepSkyBlue'></i><br>
        </div>
          """
         
    m.get_root().html.add_child(folium.Element(legend_html))

    m.save(name_plot)
