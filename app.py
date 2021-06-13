#!/usr/bin/python3
from models import *
import mysql.connector
from flask import Flask, Response, render_template, request, jsonify
import json
import numpy as np
import cv2
import base64
import pandas as pd
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://root@localhost/vehicle"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.secret_key = 'Allah'

db.init_app(app)
mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='vehicle')

def fetchDataframe():
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT * from data LEFT JOIN results ON data.frame_id=results.frame_id ORDER by data.frame_id desc limit 100")
    result = mycursor.fetchall()
    df = pd.DataFrame({
        "date": [i[2] for i in result],
        "frame_id": [i[4] for i in result],
        "vehicle": [i[5] for i in result],
        "id": [i[5] for i in result],
        "lable": [i[7] for i in result]})
    return df


def data_check(df, name):
    try:
        return df[name]
    except:
        return 0


def bar_data(df):
    df = df.lable.value_counts()
    return [
        [1, data_check(df, 'Car')],
        [2, data_check(df, "Bus")],
        [3, data_check(df, "Motorcycle")],
        [4, data_check(df, "Van")],
        [5, data_check(df, "Truck")],
        [6, data_check(df, "Bicycle")],
        [7, data_check(df, "Auto_rikshaw")]
    ]


def donut_data(df):
    df = df.lable.value_counts()
    s = sum(df.values)
    return [
        {
            'label': 'Car',
            'data': int((data_check(df, "Car")/s)*100),
            'color': '#3c8dbc'
        },
        {
            'label': 'Bus',
            'data': int((data_check(df, "Bus")/s)*100),
            'color': '#0073b7'
        },
        {
            'label': 'Truck',
            'data': int((data_check(df, "Truck")/s)*100),
            'color': '#737CA1'
        },
        {
            'label': 'Bike',
            'data': int((data_check(df, "Motorcycle")/s)*100),
            'color': '#6D7B8D'
        },
        {
            'label': 'Cycle',
            'data': int((data_check(df, "Bicycle")/s)*100),
            'color': '#566D7E'
        },
        {
            'label': 'Rikshaw',
            'data': int((data_check(df, "Auto_rikshaw")/s)*100),
            'color': '#00c0ef'
        },
        {
            'label': "Van",
            'data': int((data_check(df, "Van")/s)*100),
            'color': '#6D7B8D'
        }

    ]


def line_plot(df):
    dt = df[['date', 'id']].groupby(by='date').count()
    d = pd.DatetimeIndex(dt.index)
    year, month, day, hour, minute, second = [], [], [], [], [], []

    for i in d:
        Y = i.year
        M = i.month
        D = i.day
        h = i.hour
        m = i.minute
        s = i.second
        year.append(Y)
        month.append(M)
        day.append(D)
        hour.append(h)
        minute.append(m)
        second.append(s)
    value = [int(i) for i in dt.id.values]
    return year, month, day, hour, minute, second, value, len(dt.id.values)


@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template("index.html", jsondata=get_json())


def send_result(response=None, error='', status=200):
    if response is None:
        response = {}
    result = json.dumps({'result': response, 'error': error})
    return Response(status=status, mimetype="application/json", response=result)


@app.route('/fetchdata', methods=["POST"])
def get_json():
    df = fetchDataframe()
    bar = bar_data(df)
    donut = donut_data(df)
    year, month, day, hour, minute, second, index, ln = line_plot(df)
    return jsonify({
        "bar_data": str(bar),
        "donut_data": donut,
        "year": year[0],
        "month": month[0],
        "day": day[0],
        "hour": hour[0],
        "minute": minute[0],
        "second": second[0],
        "line_index_data": index[0],
        'count': str(np.random.random(1))
    })


@app.route("/upload", methods=['POST'])
def login():
    if request.method == 'POST':
        try:
            img_str = request.json['image']
            path = request.json["path"]
            camera_id = request.json['camera_id']
            camera_loc = request.json['camera_loc']
            results = request.json['results']

            jpg_original = base64.b64decode(img_str)
            jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
            img = cv2.imdecode(jpg_as_np, flags=1)

            a = Data(camera_id=camera_id,
                     camera_loc=camera_loc, image_path=path)
            db.session.add(a)
            db.session.flush()
            cv2.imwrite(f"static/img/output.jpg", img)
            cv2.imwrite(f"images/frames/{a.frame_id}.jpg",
                        img, [int(cv2.IMWRITE_JPEG_QUALITY), 9])

            for r in results:
                lbl = r['label']
                prob = r['prob']
                x = r['x']
                y = r['y']
                w = r['w']
                h = r['h']
                p = Result(frame_id=a.frame_id, label=lbl,
                           prob=prob, x=x, y=y, w=w, h=h)
                db.session.add(p)
                db.session.flush()

            db.session.commit()
            return send_result("Frame inserted success", status=201)
        except KeyError as e:
            return send_result(error=f'An "image" file is required {e}', status=422)
        except Exception as e:
            return send_result(error=f'Error {e}', status=500)


if __name__ == "__main__":
    app.run(debug=True)
