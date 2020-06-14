import json
import math
import os
import sqlite3

import geojson
import requests
from shapely.geometry import Polygon
from shapely.wkt import loads

dirname = os.path.dirname(__file__)
dbpath = os.path.join(dirname, "./PLZ.db")

def geocode(address):
    '''
    Input: An address

    Output: Coordinates of relevant address
    '''

    url = 'https://nominatim.openstreetmap.org/search?format=json&q=%s' % (address)
    results = json.loads(requests.get(url).text)
    lat, lon = results[0]["lat"], results[0]["lon"]

    return float(lat), float(lon)


def radius_wkt(lat,lon,radius):
    '''
    Input: Coordinates of the address at the center of the radius and the radius in km

    Output: A WKT poylgon representing the radius
    '''

    normal_polygon = [[0,0.008983204953],[0.0006266367004,0.008961322318],[0.00125022049,0.00889578102],[0.001867713331,0.008786900372],[0.00247610686,0.008635210828],[0.003072437046,0.008441451406],[0.003653798627,0.00820656608],[0.004217359268,0.00793169919],[0.004760373359,0.007618189858],[0.00528019539,0.007267565471],[0.005774292839,0.006881534236],[0.006240258514,0.006461976858],[0.006675822277,0.006010937378],[0.007078862105,0.005530613215],[0.007447414428,0.00502334446],[0.007779683697,0.004491602477],[0.008074051129,0.003937977857],[0.008329082595,0.003365167806],[0.008543535608,0.002775962995],[0.008716365375,0.002173233971],[0.008846729885,0.00155991717],[0.008933994017,0.000939000609],[0.008977732628,0.0003135093317],[0.008977732628,-0.0003135093317],[0.008933994017,-0.000939000609],[0.008846729885,-0.00155991717],[0.008716365375,-0.002173233971],[0.008543535608,-0.002775962995],[0.008329082595,-0.003365167806],[0.008074051129,-0.003937977857],[0.007779683697,-0.004491602477],[0.007447414428,-0.00502334446],[0.007078862105,-0.005530613215],[0.006675822277,-0.006010937377],[0.006240258514,-0.006461976858],[0.005774292839,-0.006881534236],[0.00528019539,-0.007267565471],[0.004760373359,-0.007618189858],[0.004217359268,-0.00793169919],[0.003653798627,-0.00820656608],[0.003072437046,-0.008441451406],[0.00247610686,-0.008635210828],[0.001867713331,-0.008786900372],[0.00125022049,-0.00889578102],[0.0006266367004,-0.008961322318],[0.00E+00,-0.008983204953],[-0.0006266367004,-0.008961322318],[-0.00125022049,-0.00889578102],[-0.001867713331,-0.008786900372],[-0.00247610686,-0.008635210828],[-0.003072437046,-0.008441451406],[-0.003653798627,-0.00820656608],[-0.004217359268,-0.00793169919],[-0.004760373359,-0.007618189858],[-0.00528019539,-0.007267565471],[-0.005774292839,-0.006881534236],[-0.006240258514,-0.006461976858],[-0.006675822277,-0.006010937377],[-0.007078862105,-0.005530613215],[-0.007447414428,-0.00502334446],[-0.007779683697,-0.004491602477],[-0.008074051129,-0.003937977857],[-0.008329082595,-0.003365167806],[-0.008543535608,-0.002775962995],[-0.008716365375,-0.002173233971],[-0.008846729885,-0.00155991717],[-0.008933994017,-0.000939000609],[-0.008977732628,-0.0003135093317],[-0.008977732628,0.0003135093317],[-0.008933994017,0.000939000609],[-0.008846729885,0.00155991717],[-0.008716365375,0.002173233971],[-0.008543535608,0.002775962995],[-0.008329082595,0.003365167806],[-0.008074051129,0.003937977857],[-0.007779683697,0.004491602477],[-0.007447414428,0.00502334446],[-0.007078862105,0.005530613215],[-0.006675822277,0.006010937378],[-0.006240258514,0.006461976858],[-0.005774292839,0.006881534236],[-0.00528019539,0.007267565471],[-0.004760373359,0.007618189858],[-0.004217359268,0.00793169919],[-0.003653798627,0.00820656608],[-0.003072437046,0.008441451406],[-0.00247610686,0.008635210828],[-0.001867713331,0.008786900372],[-0.00125022049,0.00889578102],[-0.0006266367004,0.008961322318],[0,0.008983204953]]
    new_polygon = [(lon + x[1] * radius * 1/math.cos(lat * math.pi / 180), lat + x[0] * radius) for x in normal_polygon]
    wkt = Polygon(new_polygon).wkt

    return wkt


def boundaries_lookup(minx,miny,maxx,maxy):
    '''
    Input: boundaries of a given polygon or multipolygon

    Output: a set of coordinates defining the relevant area for the database lookup
    '''

    searchfactor = 30

    lat1 = maxy + 0.008983204953 *  searchfactor
    lat2 = miny - 0.008983204953 * searchfactor
    lon1 = maxx + 0.008983204953 *  1/math.cos(maxy * math.pi / 180) * searchfactor
    lon2 = minx - 0.008983204953 *  1/math.cos(miny * math.pi / 180) * searchfactor

    return lat1,lat2,lon1,lon2


def db_lookup(lat1,lat2,lon1,lon2):
    '''
    Input: Coordinates of the search box as defined by boundaries_lookup

    Output: All zip-codes in the relevant area
    '''

    con = sqlite3.connect(dbpath)
    cur = con.cursor()
    sql = "SELECT * FROM PLZDE WHERE ? > lat_centroid AND lat_centroid > ? AND ? > lon_centroid AND lon_centroid > ?"
    cur.execute(sql, (lat1,lat2,lon1,lon2))

    lookup = cur.fetchall()

    con.commit()
    con.close()

    return lookup


def create_geojson(poly_wkt):
    '''
    Input: WKT polygon

    Output: A geojson to be displayed by folium
    '''

    polygon = loads(poly_wkt) # create shapley geometry form WKT

    a,b,c,d = polygon.bounds

    boundaries = boundaries_lookup(a,b,c,d) # determine the values for the database look up

    plz = db_lookup(*boundaries) # returns the list of relevant postcodes, area names and polygons

    results_list = [] # generating the results list

    for i in plz:
        postcode = i[0]
        postcode_name = i[1]
        postcode_polygon = loads(i[2])
        if postcode_polygon.intersects(polygon):
            overlap = postcode_polygon.intersection(polygon).area/postcode_polygon.area
            results_list.append(geojson.Feature(geometry=postcode_polygon, properties={"postcode":postcode, "overlap": overlap, "overlapstr":'{:.1%}'.format(overlap), "name": postcode_name.encode('cp1252').decode('utf8'), "centroid": (postcode_polygon.centroid.y,postcode_polygon.centroid.x)}))

    input_center = polygon.centroid
    input_polygon = geojson.Feature(geometry=polygon, properties={"postcode":00000, "overlap": 1, "name": "input"})
    areas =  sorted(results_list, key= lambda x: x["properties"]["overlap"])

    return input_polygon, input_center, areas


