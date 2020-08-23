from flask import Flask, render_template, request

import calc
import mapper
import guru as g

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/polygo",methods=['GET', 'POST'])
def polygo():

    address_input = request.args.get("address")
    radius_input = request.args.get("radius")
    polygon_input = request.form.get("polygon")

    if polygon_input:
        try:
            mapper.create_map(*calc.create_geojson(polygon_input), polygon_input)
        except:
            return render_template("alert.html")

        return mapper.create_map(*calc.create_geojson(polygon_input), polygon_input)


    if address_input and radius_input:
        try:
            coords = calc.geocode(address_input)
            float(radius_input)
        except:
            return render_template("alert.html")

        polygon_input = calc.radius_wkt(*coords, float(radius_input))

        return mapper.create_map(*calc.create_geojson(polygon_input), polygon_input, address_input, radius_input)

    return render_template("basemap.html")
