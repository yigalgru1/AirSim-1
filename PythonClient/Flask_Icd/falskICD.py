import enum
from datetime import datetime
from flask import Flask, Response, render_template, request, jsonify
from flask_socketio import SocketIO, emit, send
import airsim
import numpy as np
import math
import time
import sys
import base64
# koby
# iris123456

from threading import Thread
import threading

import json
# Config from filepath in env
app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.cfg')
print("read config file")

unitypot = int(app.config["SESSION_COOKIE_PATH"])
print(unitypot)
print("complit read config file")

app = Flask(__name__)
socketio = SocketIO(app, ping_timeout=100, ping_interval=100)


hot_point_ned_coordinate = []
way_point_ned_coordinate = []
way_point_status = -1
camInfo = None
is_armed = False
air_sim = None
air_sim2 = None
stop_threads1 = None
stop_threads2 = None
workers = []
# unityDronePort = 41451
initialize_height = 0

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


@app.route('/button_press')
def button_press():
    print('In SomeFunction')
    return "Nothing"


@app.route('/form', methods=['GET', 'POST'])
def form():
    data = request.get_json()
    return "Nothing"


@app.route('/addRegion', methods=['POST'])
def addRegion():

    # return (request.form['projectFilePath'])
    return "Nothing"

#   missing
# ========================================================================== #
@app.route('/ICD/', methods=['GET', 'POST'])
def ICD():
    render_template('index.html')


#   Takeoff
# ========================================================================== #
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
            # print(unityDronePort)
            initializeHeight()

            thread = Thread(target=takeoff_operation, kwargs={
                            'value': request.args.get('value', operation)})
            thread.start()

            respons = {"success": True, "message": ""}
            return jsonify(respons)
        else:
            print(msg)
            respons = {"success": False, "message": msg}
            return jsonify(respons)


def takeoff_operation(value):
    import takeoff
    from takeoff import Takeoff
    _task = Takeoff(value, unitypot)
    _task.start()


#   Land
# ========================================================================== #
@app.route('/land', methods=['GET', 'POST'])
def land():
    if request.method == "POST":
        import sys
        sys.path.insert(1, '../icd_multirotor')
        thread = Thread(target=land_operation)
        thread.start()
        respons = {"success": True, "message": ""}
        return jsonify(respons)


def land_operation():
    import land
    from land import Land
    _task = Land(unitypot)

    time.sleep(1)
    _task.start()
    global is_armed
    is_armed = False

# HotPoint
#
# Body:
# {	  "latitude": 32.8004,
#     "longitude": 35.05148,
#     "altitude":22,
#     "radius":20,
#     "angular_speed": 5,
#     "is_clockwise": 0,
#     "start_point": 0,
#     "yaw_mode": 2
#  }
# ========================================================================== #
@app.route('/hotPoint/upload', methods=['GET', 'POST'])
def hotPoint():
    if request.method == "POST":
        data = request.get_json()
        print("request")
        msg = "data is missing !"
        if data:
            import sys
            sys.path.insert(1, '../icd_multirotor')
            coordinates = []
            coordinates = [data['latitude'], data['longitude'],
                           data['altitude']]  # get lon\lat
            global hot_point_ned_coordinate
            ned_coordinates = geo_to_ned(coordinates)

            global initialize_height
            z1 = data['altitude']
            z1 = initialize_height - z1
            print("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF")
            print(data['latitude'])
            print(data['longitude'])
            print(data['altitude'])
            hot_point_ned_coordinate = [
                ned_coordinates[0], ned_coordinates[1], -(z1)]  # TODO:: hieght
            respons = {"success": True, "message": ""}
            return jsonify(respons)
        else:
            print(msg)
            respons = {"success": False, "message": msg}
            return jsonify(respons)


# hotPoint Action
#
# Body:
# {
#   "action": 0/1/2/3
# }
# ========================================================================== #
@app.route('/hotPoint/action', methods=['GET', 'POST'])
def hotPointAction():
    if request.method == "POST":
        data = request.get_json()
        msg = "action data is missing !"
        if data:
            import sys
            sys.path.insert(1, '../icd_multirotor')
            action = data['action']
            if (action == 0):
                thread = Thread(target=hotpoint_action_operation)
                thread.start()

            respons = {"success": True, "message": ""}
            return jsonify(respons)
        else:
            print(msg)
            respons = {"success": False, "message": msg}
            return jsonify(respons)


def hotpoint_action_operation():
    import hotPoint
    from hotPoint import HotPoint
    # global param....
    _task = HotPoint(
        hot_point_ned_coordinate[0], hot_point_ned_coordinate[1], hot_point_ned_coordinate[2], unitypot)
    _task.start()


# WayPoints uploadComplex
#
# {
# 	"action_on_finish": 0,
# 	"points": [
#	 	{
#	 		"latitude": 32.922820,
#	 		"longitude": 35.28677496,
#	 		"altitude": 6,
#	 		"velocity": 10,
#	 		"yaw": 90
#	 	},
#	 	{
#	 		"latitude": 32.922020,
#	 		"longitude": 35.28707496,
#	 		"altitude": 6,
#	 		"velocity": 10,
#	 		"yaw": 90
#	 	},
#	 		 	{
#	 		"latitude": 32.921820,
#	 		"longitude": 35.28777496,
#	 		"altitude": 6,
#	 		"velocity": 10,
#	 		"yaw": 90
#	 	}
# 	]
# }
# ========================================================================== #
@app.route('/wayPoint/uploadComplex', methods=['GET', 'POST'])
def wayPoints():
    if request.method == "POST":
        data = request.get_json()
        print("request")
        msg = "data is missing !"
        if data:
            import sys
            sys.path.insert(1, '../icd_multirotor')
            points = data['points']

            global initialize_height
            print("!!!!!!!!!!!!!")
            print(initialize_height)
            path = []
            array_length = len(points)
            for i in range(array_length):
                point = points[i]  # {X,Y,Z}
                x = point['latitude']
                y = point['longitude']
                z = point['altitude']  # add the const value {20}
                z = initialize_height - z
                print(z)
                geo_point = []
                geo_point = [x, y, z]
                print(geo_point)
                ned_coordinate = geo_to_ned(geo_point)
                airSimPoint = airsim.Vector3r(
                    ned_coordinate[0], ned_coordinate[1], z)
                path.append(airSimPoint)

            global way_point_ned_coordinate
            way_point_ned_coordinate = path

            respons = {"success": True, "message": ""}
            return jsonify(respons)
        else:
            print(msg)
            respons = {"success": False, "message": msg}
            return jsonify(respons)


#  WayPoints upload
#
#  {
#   "latitude0": 32.908424,
#   "longitude0": 35.293166,
#   "latitude1": 32.908424,
#   "longitude1": 35.293166,
#   "altitude": 30
#  }
# ========================================================================== #
@app.route('/wayPoint/upload', methods=['GET', 'POST'])
def wayPointUpload():
    if request.method == "POST":
        data = request.get_json()
        print("request")
        msg = "data is missing !"
        if data:
            import sys
            sys.path.insert(1, '../icd_multirotor')
            path = []
            x1 = data['latitude0']
            y1 = data['longitude0']
            z1 = data['altitude']  # they send cons value {20}
            x2 = data['latitude1']
            y2 = data['longitude1']

            global initialize_height
            z1 = initialize_height - z1

            geo_point1 = []
            geo_point1 = [x1, y1, z1]
            ned_coordinate1 = geo_to_ned(geo_point1)
            airSimPoint1 = airsim.Vector3r(
                ned_coordinate1[0], ned_coordinate1[1], z1)
            path.append(airSimPoint1)
            geo_point2 = []
            geo_point2 = [x2, y2, z1]
            ned_coordinate2 = geo_to_ned(geo_point2)
            airSimPoint2 = airsim.Vector3r(
                ned_coordinate2[0], ned_coordinate2[1], z1)
            path.append(airSimPoint2)

            global way_point_ned_coordinate
            way_point_ned_coordinate = path

            respons = {"success": True, "message": ""}
            return jsonify(respons)
        else:
            print(msg)
            respons = {"success": False, "message": msg}
            return jsonify(respons)


# wayPoint Action
#
# Body:
# {
#   "action": 0/1/2/3
# }
# ========================================================================== #
@app.route('/wayPoint/action', methods=['GET', 'POST'])
def wayPointAction():
    if request.method == "POST":
        data = request.get_json()
        msg = "action data is missing !"
        if data:
            import sys
            sys.path.insert(1, '../icd_multirotor')
            action = data['action']
            global way_point_status
            if (action == 0):
                way_point_status = 0
                print(way_point_ned_coordinate)
                thread = Thread(target=waypoint_action_operation)
                thread.start()
            elif (action == 1):
                way_point_status = 1
            elif (action == 2):
                way_point_status = 2
            elif (action == 3):
                way_point_status = 3

            respons = {"success": True, "message": ""}
            return jsonify(respons)
        else:
            print(msg)
            respons = {"success": False, "message": msg}
            return jsonify(respons)


def waypoint_action_operation():
    import wayPoints
    from wayPoints import WayPoints
    global way_point_status
    print(way_point_ned_coordinate)
    _task = WayPoints(way_point_ned_coordinate, 12, unitypot)
    _task.start()
    way_point_status = 1


#   position_set
#
#  {
#	"x": 20,
#	"y": 20,
#	"z": 25,
#	"tolerance": 2
# }
# ========================================================================== #
@app.route('/position_set', methods=['GET', 'POST'])
def positionSet():
    if request.method == "POST":
        data = request.get_json()
        print("request")
        x = data['x']
        y = data['y']
        z = data['z']
        ned_coordinates = [x, y, z]

        msg = "NED is missing"
        if ned_coordinates:
            import sys
            sys.path.insert(1, '../icd_multirotor')

            thread = Thread(target=position_set_operation, kwargs={
                            'value': request.args.get('value', ned_coordinates)})
            thread.start()

            respons = {"success": True, "message": ""}
            return jsonify(respons)
        else:
            print(msg)
            respons = {"success": False, "message": msg}
            return jsonify(respons)


def position_set_operation(value):
    import positionSet
    from positionSet import PositionSet
    _task = PositionSet(value[0], value[1], value[2], unitypot)
    _task.start()
####

#   gimbal_set
#
# {
# 	"yaw": 0,
# 	"pitch": 0,
# 	"roll": 0
# }
# }
# ========================================================================== #
@app.route('/gimbal/set', methods=['GET', 'POST'])
def gimbalSet():
    if request.method == "POST":
        data = request.get_json()
        print("request")
        yaw = data['yaw']
        pitch = data['pitch']
        roll = data['roll']
        rotation = [yaw, pitch, roll]
        msg = "rotation is missing"
        if rotation:
            import sys
            sys.path.insert(1, '../icd_multirotor')

            thread = Thread(target=gimbal_set_operation, kwargs={
                            'value': request.args.get('value', rotation)})
            thread.start()

            respons = {"success": True, "message": ""}
            return jsonify(respons)
        else:
            print(msg)
            respons = {"success": False, "message": msg}
            return jsonify(respons)


def gimbal_set_operation(value):
    import gimbal_set
    from gimbal_set import Gimbal
    _task = Gimbal(value[0], value[1], value[2], unitypot)
    _task.start()

####

#   WebSocket -> start !
# ========================================================================== #
@app.route('/api/WebSocket/start', methods=['GET'])
def WebSocketStart():
    if request.method == "GET":
        print("GET /WebSocket/start")
        time.sleep(1)
        global stop_threads1
        global stop_threads2
        global workers
        stop_threads1 = False
        stop_threads2 = False

        # call a image send function in other thread
        imageThread = threading.Thread(
            target=sendImage_action_operation, args=(id, lambda: stop_threads1))
        imageThread.start()
        # # call a telemetry send function in other thread
        telemetryThread = threading.Thread(
            target=sendTelemetry_action_operation, args=(id, lambda: stop_threads2))
        workers.append(telemetryThread)
        workers.append(imageThread)
        telemetryThread.start()
        respons = {"success": True, "message": "WebSocket start"}
        return jsonify(respons)


#   WebSocket -> start !
# ========================================================================== #


def sendImage_action_operation(id, stop):
    global air_sim2
    air_sim2 = init_airsim()
    while True:
        if stop():
            print("  Exiting loop.")
            air_sim2.armDisarm(False)
            air_sim2.reset()
            air_sim2.enableApiControl(False)
            print('STOP send images')
            break
        data = load_image(air_sim2)
        print('send image')
        socketio.emit('image', data, broadcast=True)
        time.sleep(0.1)


def sendTelemetry_action_operation(id, stop):
    global air_sim
    air_sim = init_airsim()

    while True:
        if stop():
            print("  Exiting loop.")
            air_sim.armDisarm(False)
            air_sim.reset()
            air_sim.enableApiControl(False)
            print('STOP send telemetry')
            break
        data = load_airsim(air_sim)
        print('send telemetry')
        socketio.emit('my', data, broadcast=True)
        time.sleep(1)



 ##combine websockets
 # 
 # def sendTelemetry_action_operation(id, stop):
    # global air_sim
    # air_sim = init_airsim()
    # counter = 0
    # global 
    # interval = 0.1
    # while True:
    #     if stop():
    #         print("  Exiting loop.")
    #         air_sim.armDisarm(False)
    #         air_sim.reset()
    #         air_sim.enableApiControl(False)
    #         print('STOP send telemetry')
    #         break
    #     counter = round(counter + interval, 2)
    #     if counter == 1:
    #         data = load_airsim(air_sim)
    #         print('send telemetry')
    #         socketio.emit('my', data, broadcast=True)
    #         counter = 0
    #     imageData = load_image(air_sim)
    #     print('send image')
    #     socketio.emit('image', imageData, broadcast=True)
    #     time.sleep(0.1)       


#   initialize the client.
# ========================================================================== #
def init_airsim():
    # global unityDronePort
    print(unitypot)
    airsim_client = airsim.MultirotorClient('', unitypot, 3600)
    # airsim_client = airsim.MultirotorClient()
    airsim_client.confirmConnection()
    airsim_client.enableApiControl(True)
    airsim_client.armDisarm(True)
    return airsim_client


#   initialize the client.
# ========================================================================== #
def initializeHeight():
    global air_sim
    global initialize_height
    global is_armed
    rpcinfo = air_sim.getMultirotorState()
    kinematics_estimated = rpcinfo.kinematics_estimated
    initialize_height = kinematics_estimated.position.z_val
    is_armed = True

#   get current kinematics_estimated.
# ========================================================================== #


def get_kinematics_estimated():
    global air_sim
    rpcinfo = air_sim.getMultirotorState()
    kinematics_estimated = rpcinfo.kinematics_estimated
    return (kinematics_estimated)

#   get current gps_location
# ========================================================================== #


def get_gps_location():
    global air_sim
    rpcinfo = air_sim.getMultirotorState()
    gps_location = rpcinfo.gps_location
    return (gps_location)


#   load telmetry
# ========================================================================== #
def load_airsim(airsim_client):
    rpcinfo = airsim_client.getMultirotorState()
    gps_location = rpcinfo.gps_location
    kinematics_estimated = rpcinfo.kinematics_estimated
    # pitch, roll, yaw = airsim.to_eularian_angles(
    #     rpcinfo.kinematics_estimated.orientation)

    global camInfo
    camInfo = airsim_client.simGetCameraInfo("0")
    pitch, roll, yaw = airsim.to_eularian_angles(camInfo.pose.orientation)
    homepoint = airsim_client.getHomeGeoPoint()
    global way_point_status
    global initialize_height
    if(initialize_height is not 0):
        height_above_takeoff = - \
            (kinematics_estimated.position.z_val) + initialize_height
    else:
        height_above_takeoff = initialize_height
    telemetry = {
        "battery_state": {
            "percentage": 70.04
        },
        "distance_from_home": 1561.4,
        "gimbal": {
            "roll": roll,
            "pitch": pitch,
            "yaw": yaw
        },
        "height_above_takeoff": height_above_takeoff,
        "gps_health": 5,
        "heading": math.degrees(yaw),
        "velocity": {
            "x": kinematics_estimated.linear_velocity.x_val,
            "y": kinematics_estimated.linear_velocity.y_val,
            "z": kinematics_estimated.linear_velocity.z_val
        },
        "gps_position": {
            "latitude": gps_location.latitude,
            "altitude": gps_location.altitude,
            "longitude": gps_location.longitude
        },
        "last_change_time": rpcinfo.timestamp,
        "lastHome": {
            "latitude": homepoint.latitude,
            "operationalAlt": homepoint.altitude,
            "longitude": homepoint.longitude
        },
        "owner": "droneService",
        "state": {
            "armed": is_armed
        },
        "wayPoints": {
            "status": way_point_status
        },
        "keepAlive": rpcinfo.timestamp
    }
    return telemetry


#   WebSocket -> end !
# ========================================================================== #
@app.route('/api/WebSocket/end', methods=['GET'])
def WebSocketEnd():
    if request.method == "GET":
        global stop_threads1
        global stop_threads2
        print("GET /WebSocket/end")
        stop_threads1 = True
        stop_threads2 = True
        global workers
        for worker in workers:
            worker.join()
        respons = {"success": True, "message": "WebSocket end"}
        return jsonify(respons)

#   load image
# ========================================================================== #


def load_image(airsim_client):
    rawImage = airsim_client.simGetImage("0", airsim.ImageType.Scene)
    image64 = base64.b64encode(rawImage).decode("utf-8")
    return image64




@app.route('/fov', methods=['GET', 'POST'])
def fov():
    if request.method == "POST":
        import sys
        sys.path.insert(1, '../icd_multirotor')
        thread = Thread(target=fov_operation)
        thread.start()
        respons = {"success": True, "message": ""}
        return jsonify(respons)


def fov_operation():
    import fov
    from fov import Fov
    _task = Fov(unitypot)
    _task.start()


# ========================================================================== #
# ############################# Socket.io ################################## #
# ========================================================================== #
@socketio.on('connect')
def WSocketConnect():
    print('connect')


@socketio.on('disconnect')
def WSocketDisconnect():
    print('disconnect')


@socketio.on('keepAlive')
def WSocketHandleKeepAlive(json):
    # print('received keepAlive: ' + str(json))
    pass


@socketio.on('my')
def handle_my_custom_event(json):
    print('received my: ' + str(json))


@socketio.on('image')
def handle_image_custom_event(json):
    print('received image: ' + str(json))


@socketio.on('force_send')
def handle_force_send(json):
    print('received force_send: ' + str(json))


@socketio.on('force_stop')
def handle_force_stop(json):
    print('received force_stop: ' + str(json))


# geo_to_ned
#
# geodetic coordinate to local (unity units)
def geo_to_ned(gps_location):
    global air_sim
    home_point = air_sim.getHomeGeoPoint()
    d_lat = gps_location[0] - home_point.latitude
    d_lon = gps_location[1] - home_point.longitude
    if (gps_location[2] > home_point.altitude):
        d_alt = gps_location[2] - home_point.altitude
    else:
        d_alt = home_point.altitude - gps_location[2]

    radian = np.deg2rad(d_lat)
    x = radian * 6378137.0  # 6378137.0f = earth_radius
    y = np.deg2rad(d_lon) * 6378137.0 * math.cos(np.deg2rad(gps_location[1]))
    ned_coordinates = []
    ned_coordinates = [x, y, d_alt]

    print(ned_coordinates[0])
    print(ned_coordinates[1])
    print(ned_coordinates[2])
    return (ned_coordinates)


# if __name__ == '__main__':
#     flaskPortStr = "/flaskPortArg="
#     unityDronePortStr = "/unityDronePort="
#     for i in range(1, len(sys.argv)):
#         if sys.argv[i].startswith(flaskPortStr):
#             flaskp = sys.argv[i][len(flaskPortStr):]
#             app.config['flaskPortStr'] = flaskp
#             #flaskport = sys.argv[i][len(flaskPortStr):]
#             print(flaskp)
#         elif sys.argv[i].startswith(unityDronePortStr):
#             #unityDronePort = int(sys.argv[i][len(unityDronePortStr):])
#             uport = int(sys.argv[i][len(unityDronePortStr):])
#             app.config['unityDronePort']  = uport
#             print(unityDronePort)
#         print(sys.argv[i])
#     app.run(host='0.0.0.0', port=flaskp, debug=True)


# if __name__ == '__main__':
#    app.run(host='0.0.0.0',debug=True)
#    socketio.run(app)
