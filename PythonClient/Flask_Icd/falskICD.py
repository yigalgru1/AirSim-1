

import enum
from flask import request
from datetime import datetime
from flask import Flask, render_template, request, jsonify

import json
app = Flask(__name__)

posts = [{
    'author': "yigal",
    'title': "1",
    'content': "First post content",

}, {
    'author': "pigal",
    'title': "2",
    'content': "Second post content",
}]


@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template('index.html',
                           posts=posts,
                           title='Contact',
                           year=datetime.now().year,
                           message='Your contact page.')


@app.route('/SomeFunction')
def SomeFunction():
    print('In SomeFunction')
    return "Nothing"

# import requests
# res = requests.post('http://localhost:5000/api/add_message/1234',
# json={"mytext":"lalala"})


@app.route('/button_press')
def button_press():
    print('In SomeFunction')
    return "Nothing"


@app.route('/form', methods=['GET', 'POST'])
def form():
    data = request.get_json()
    return "Nothing"


class ICDOperation(enum.Enum):
    # TakeOff = "takeoff"
    # MoveToPosition = "moveToPosition"
    # Land = "land",
    # RotateToYaw = "rotateToYaw",
    # Gimbal = "gimbal"
    TakeOff = 1
    MoveToPosition = 2
    RotateToYaw = 3
    Gimbal = 4
    Land = 5


Daytype = {}
Daytype[ICDOperation.TakeOff] = 'takeoff'
Daytype[ICDOperation.MoveToPosition] = 'moveToPosition'
Daytype[ICDOperation.Land] = 'land'
Daytype[ICDOperation.RotateToYaw] = 'rotateToYaw'
Daytype[ICDOperation.Gimbal] = 'gimbal'


@app.route('/addRegion', methods=['POST'])
def addRegion():

    # return (request.form['projectFilePath'])
    return "Nothing"


@app.route('/ICD/', methods=['GET', 'POST'])
def ICD():
    if request.method == "POST":
        data = request.get_json()
        print("request")
        operation = data['operation']
        print(operation)
        import sys
      #  sys.path.insert(1, 'D:\Git\AirSim\PythonClient\icd_multirotor')
        sys.path.insert(1, '../icd_multirotor')
        if operation == Daytype[ICDOperation.TakeOff]:
            import takeoff
        elif operation == Daytype[ICDOperation.Land]:
            print("land action")
            import land
        elif operation == Daytype[ICDOperation.MoveToPosition]:
            coordinates = data['coordinates']
            import moveToPosition
            from moveToPosition import MoveToPosition
            r = MoveToPosition(
                coordinates[0], coordinates[1], coordinates[2])
            r.start()
        elif operation == Daytype[ICDOperation.RotateToYaw]:
            import rotateToYaw
            from rotateToYaw import RotateToYaw
            angle = data['angle']
            print(angle)
            r = RotateToYaw(angle)
            r.start()
        elif operation == Daytype[ICDOperation.Gimbal]:
            import gimbal
        return render_template('index.html')


@app.route('/takeoff', methods=['GET', 'POST'])
def takeoff():
    if request.method == "POST":
        data = request.get_json()
        print("request")
        operation = data['operationalAlt']
        msg = "missing Alt operand"
        if operation:
            import sys
            sys.path.insert(1, '../icd_multirotor')
            import takeoff
            from takeoff import Takeoff
            print(data)
            r2 = Takeoff(operation)
            result = r2.start()
            if result == True:

                respons = {"success": True, "message": ""}
                return jsonify(respons)
            else:
                msg = "got error as collision"
                respons = {"success": False, "message": msg}
                return jsonify(respons)
        else:
            print(msg)
            respons = {"success": False, "message": msg}
            return jsonify(respons)


@app.route('/land', methods=['GET', 'POST'])
def land():
    if request.method == "POST":
        import sys
        sys.path.insert(1, '../icd_multirotor')
        import land
        from land import Land
        r2 = Land()
        result = r2.start()
        if result == True:
            respons = {"success": True, "message": ""}
            return jsonify(respons)
        else:
            msg = "got error as collision"
            respons = {"success": False, "message": msg}
            return jsonify(respons)


if __name__ == '__main__':
    app.run(debug=True)
