import re

import folium
from folium.features import DivIcon

def create_map(polygon_input,input_center,areas, polygon_wkt, address = "", radius = ""):
    '''
    Input: the polygon submitted, the centroid of the polygon, the geojson of all areas intersecting the submitted polygon, submitted polygon as wkt

    Output: text in html format rendering a map displaying the polygon and intersected areas
    '''

    m = folium.Map(
        location= (input_center.coords[0][1],input_center.coords[0][0]),
        zoom_start= 11
        )
    folium.GeoJson(
            polygon_input,
            control=False,
            name= "Radius",
            style_function= lambda x: {
                "weight": 2.5,
                "fillColor": "white",
                "color": "red",
                "fillOpacity": 0.2
            }
            ).add_to(m)

    for feature in areas:

        folium.GeoJson(
            feature,
            control=False,
            style_function= lambda x: {
                'fillColor': "grey",
                'weight': 1.5,
                "fillOpacity": 0.2,
                "color":"grey",
                "opacity": 0.7
            },
        ).add_to(m)

        folium.GeoJson(
            feature,
            name= feature["properties"]["postcode"] + ": "+ '{:.1%}'.format(feature["properties"]["overlap"]),
            tooltip=folium.GeoJsonTooltip(fields = ["name","postcode","overlapstr"], labels=False, sticky=False),
            style_function= lambda x: {
                'fillColor': "rgba(0,122,255,1)",
                'weight': 1.5,
                "fillOpacity": 0.2,
                "color":"grey",
                "opacity": 0.8
            },
            highlight_function=lambda x: {
                'fillColor': "grey"}
        ).add_to(m)

        folium.Marker(feature["properties"]["centroid"],
        icon=DivIcon(
            icon_size=(150,36),
            icon_anchor=(15,0),
            html=f'''<div style="
            font-size: 11pt;
            font-weight: bold;
            text-shadow: -1px 0 white, 0 1px white, 1px 0 white, 0 -1px white;
            color: grey;
            opacity: 0.8
            ">
            {feature["properties"]["postcode"]}</div>''',
        )).add_to(m)

    folium.GeoJson(
        polygon_input,
        name= "Radius",
        style_function= lambda x: {
            "weight": 1.5,
            "fillColor": "rgba(250, 0, 175, 0.3)",
            "color": "white",
            "fillOpacity": 0.2
        }
        ).add_to(m)



    folium.LayerControl().add_to(m)

    html_string = m.get_root().render()

    a = re.search(r"(.*)</head>",html_string, flags= re.S).group(1)
    b = re.search(r"(</head>.*)</body>",html_string, flags= re.S).group(1)
    c = re.search(r"</body>.*",html_string, flags= re.S).group(0)

    d = '''
    <link rel="icon" href="../static/icon.svg">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
    <link rel="stylesheet" type="text/css" href="../static/drag.css">
    '''

    e = f'''
    <div id="mydiv">
    <div id="mydivheader"><a href="/polygo"><img src="../static/polygo.png" alt="hello" width="120"></a></div>
    <form id="form" action="/polygo" method="GET">
        <div class="form-group">
        <input type="text" class="form-control-sm" id="form-field" name="address" value="{address}" placeholder="Address" required>
        <br>
        <input type="text"  class="form-control-sm" id="form-field" name="radius" value="{radius}" placeholder="Radius in km" required>
        <br>
        <input class="btn btn-primary btn-sm" type="submit" value="Search">
        </div>
    </form>
    <form id="form" action="/polygo" method="POST">
    <div class="form-group">
        <textarea class="form-control-sm" id="polytext" name="polygon" style ="width:250px;height: 100px;" placeholder="POLYGON((9 54,6 50,10 47,13 48,15 51,14 53,9 54))" required>{polygon_wkt}</textarea>
        <br>
        <button class="btn btn-primary btn-sm" type="button" onclick="copyText()">Copy WKT</button>
        <input class="btn btn-primary btn-sm" type="submit" value="Search">
        </div>
    </form>
    <address style="margin: 0; font-size: 10px;text-align: right;">Problems?<a href="mailto:patrick@pp83.de"> patrick@pp83.de</a></address>
    </div>
    '''
    f = '''
    <script>
            function copyText(){
            var copyText = document.getElementById("polytext");
            copyText.select();
            copyText.setSelectionRange(0, 99999)
            document.execCommand("copy");
            }
        </script>
        <script src="../static/drag.js"></script>
    '''


    new_template =  a + d + b + e + c + f

    new_template = re.sub(r'<link rel=\"stylesheet\" href=\"https://maxcdn\.bootstrapcdn\.com/bootstrap/3\.2\.0/css/bootstrap\.min\.css\"/>',r'',new_template)
    new_template = re.sub(r'<link rel=\"stylesheet\" href=\"https://maxcdn\.bootstrapcdn\.com/bootstrap/3\.2\.0/css/bootstrap-theme\.min\.css\"/>',r'',new_template)


    return new_template
