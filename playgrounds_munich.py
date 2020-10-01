import numpy as np
import json
import plotly.graph_objs as go
import geopandas as gpd
import json
import pandas as pd
from shapely.geometry import Point, Polygon, shape

### just save your mapbox_token in this file ###
mapbox_access_token = open("./files/.mapbox_token").read()


### Read and prepare shape file for mapbox (you can download it here: https://www.arcgis.com/home/item.html?id=369c18dfc10d457d9d1afb28adcc537b) ###
districts = gpd.read_file('./files/Munich_25_Bezirke_Dissolved.shp')

### save as json file for further processing ###
districts.to_file("districts_geo_json", driver="GeoJSON")
with open("districts_geo_json") as geofile:
    districts_json = json.load(geofile)


### read the playground file (you can download it here: https://www.opengov-muenchen.de/dataset/oeffentliche-spielplaetze-muenchen)
playgrounds = pd.read_csv("./files/spielplaetzemuenchenohneleerespalten2016-06-13.csv")

### create points from lon and lat
playgrounds_with_points = gpd.GeoDataFrame(
    playgrounds, geometry=gpd.points_from_xy(playgrounds.longitude, playgrounds.latitude))


#print(spielplaetze.head())
print(districts_json["features"][0].keys())
#Result: dict_keys(['type', 'properties', 'geometry'])


### add fields id for mapping and count for the sum of playgrounds ###
for k in range(len(districts_json['features'])):
    districts_json['features'][k]['id'] = k
    districts_json['features'][k]['geometry']['count'] = 0

print(districts_json["features"][0].keys())
#Result: dict_keys(['type', 'properties', 'geometry', 'id'])


#print(bezirke_json["features"][0]['properties'])

#print(bezirke_json["features"][0]['geometry']['coordinates'])

### check if the current playground is within the polygon and sum it up ###
for index, row in playgrounds_with_points.iterrows():
    #print(row['geometry'])
    for k in range(len(districts_json['features'])):
        polygon = shape((districts_json['features'][k]['geometry']))
        #print(polygon)
        if row["geometry"].within(polygon):
           districts_json['features'][k]['geometry']['count'] = districts_json['features'][k]['geometry']['count'] + 1

#print(bezirke_json["features"][0]['geometry']['count'])



### visualize it ###
z = [districts_json['features'][k]['geometry']['count'] for k in range(len(districts_json['features']))]
loc = [districts_json['features'][k]['id'] for k in range(len(districts_json['features']))]
fig = go.Figure(go.Choroplethmapbox(z=z,
                                    locations=loc,
                                    colorscale='greens',
                                    colorbar=dict(thickness=20, ticklen=3),
                                    geojson=districts_json,
                                    #text=text,
                                    hoverinfo='z',
                                    marker_line_width=1, marker_opacity=0.75))

fig.update_layout(title_text='Playgrounds in Munich',
                  title_x=0.5, width=700,  # height=700,
                  mapbox=dict(center=dict(lat=48.137154, lon=11.576124),
                              accesstoken=mapbox_access_token,
                              style='streets',
                              zoom=10,
                              ));

fig.show()