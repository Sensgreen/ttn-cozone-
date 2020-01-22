import sys, os

cwd = os.getcwd()
parentcwd = os.path.dirname(cwd)
sys.path.append(cwd)
sys.path.append(parentcwd)
print(sys.path)

import datetime
import time
from ttn import MQTTClient, ApplicationClient

# ---------- OPEN WEATHER API --------------------- #
import pyowm

from default.UplinkMessage import UplinkMessage

from threading import Thread, Lock
import threading
outsideWeather = {}
outsideWeather['temp'] = -1
outsideWeather['humidity'] = -1
def updateOutsideWeatherData():
    try:
        owm = pyowm.OWM("76b5f2963ba4337497dfd55622c5724e")  # You MUST provide a valid API key

        # Have a pro subscription? Then use:
        # owm = pyowm.OWM(API_key='your-API-key', subscription_type='pro')

        # Search for current weather in London (Great Britain)
        # Add search for current location, whichever
        observation = owm.weather_at_coords(39.9334 , 32.8597 )  # Ankara
        w = observation.get_weather()

        #print(w)  # <Weather - reference time=2013-12-18 09:20,
        # status=Clouds>

        # Weather details
        outsideWeather['temp'] = w.get_temperature('celsius')['temp']
        outsideWeather['humidity'] = w.get_humidity()
        print(outsideWeather)
        # print(w.get_wind())  # {'speed': 4.6, 'deg': 330}
        # print(w.get_humidity())  # 87
        # print(w.get_temperature('celsius')['temp'])  # {'temp_max': 10.5, 'temp': 9.7, 'temp_min': 9.0}

        # Search current weather observations in the surroundings of
        # lat=22.57W, lon=43.12S (Rio de Janeiro, BR)
        observation_list = owm.weather_around_coords(-22.57, -43.12)
    except Exception as e:
        print(e)
    threading.Timer(360, updateOutsideWeatherData).start()

weatherListenerThread = threading.Thread(target=updateOutsideWeatherData)
weatherListenerThread.daemon = True
weatherListenerThread.start()



# ---------- SENSOR - TTN MANAGEMENT -------------- #
app_id = "sensgreen_lorawan"
access_key = "ttn-account-v2.XOMEQh_XqiaweiOBdKhc1SWKws1lGkRgBqyho8mHq4Q"

# config = {
#     "apiKey": "AIzaSyDJZiu9r9kFfF6XkE4h4DTJioeVYWfvXp8",
#     "authDomain": "projectId.firebaseapp.com",
#     "databaseURL": "https://sgbeacon-42c31.firebaseio.com/",
#     "storageBucket": "sgbeacon-42c31.appspot.com"
# }

# config = {
#     "apiKey": "AIzaSyCxNgLjI0F-3Op_tJPzn7LQIF5tH1sA2oU",
#     "authDomain": "ekobina-test.firebaseapp.com",
#     "databaseURL": "https://ekobina-test.firebaseio.com",
#     "storageBucket": "ekobina-test.appspot.com"
# }
# firebase = pyrebase.initialize_app(config)
# # Get a reference to the auth service
# auth = firebase.auth()
#
# # Log the user in
# user = auth.sign_in_with_email_and_password("ekobina@ekodenge.com.tr", "1q2w3e4r")
#
# print(user)
# # Get a reference to the database service
# db = firebase.database()

import firebase_admin
import google.cloud
from firebase_admin import credentials, firestore, db

#from default.NotificationService import locationSensorNotifyForEmpty

cred = credentials.Certificate("serviceAccount.json")
default_app = firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://sensgreen-new.firebaseio.com'
})

def connect_callback(res, client):
    print("Connection Result: ", res)


def getSensorLocationPath(sensor):
    try:
        customer = sensor["customer"]  # DEFINES THE REAL LOCATION OF SENSOR such as Kolektif or Prokon etc.
        floor = sensor["floor"]
        section = sensor["section"]

        if customer and section and floor:
            return getConstructedCustomerPathFromSubPath("sensme/customers/{}/sections/{}/floors/{}/locations/".format(customer, section, floor))
    except:
        return getConstructedCustomerPathFromSubPath("sensme/locations/")


ER_FEEDBACKS = "Feedbacks/"
ER_SENSORS = "Sensors/"
ER_USERS = "Users/"

# LEARN_LOCATION_ROOT = "sensme/learn-location"
# LOCATION_PATH = "sensme/locations/"
# FEEDBACK_PATH = "sensme/user-feedbacks/"
# LEARNED_LOCATION_PATH = "sensme/learn-location/"
# USERS_PATH = "sensme/users/"
# USER_LOGIN_PATH = "last-logins/"
# USER_BEACON_PATH = "activeBeaconList"
# USER_LOCATION_PREDICTION = "lastPrediction"
# USER_LOCATION_PREDICTION_TIME = "lastPredictionTime"

SENSORS_PATH = "Sensors/"
NO_ZONE= "Data/no_zone_info/"
LOCATION_DATA="Data/"

DASHNOARD_SENSORS_PATH = "sensme/dashboard/sensors"
DASHNOARD_LOCATION_PATH = "sensme/dashboard/locations"


def getConstructedCustomerPathFromSubPath(subpath):
    global CUSTOMER_NAME
    return "Customers/" + CUSTOMER_NAME + "/" + subpath

CUSTOMER_NAME = input("Enter Customer Name: ")
#
#
sensors = db.reference(getConstructedCustomerPathFromSubPath(SENSORS_PATH)).get()
SENSOR_DEVID_LOCATION_DICT = {}
if sensors is not None:
    for key, value in sensors.items():
        print(key)
        print(value)
        SENSOR_DEVID_LOCATION_DICT[
            key] = value  # ["locationName"]  # SensId is trivial, it must be location name that we define

#print(SENSOR_DEVID_LOCATION_DICT)
DICT_DEVID_ZONENAME = {
    "v2_node_12": "Ofis",
    "test_office": "Toplanti Odasi",
    "v2_node_5": "Ofis2"
}

#TODO: Sensör 15 dakika veri göndermezse uyarı gönder telefona

def uplink_callback(msg, client):
    print("Recieved uplink: ", msg)
    msgsize = len(msg)

    try:
        uplink_message = UplinkMessage(msg, outsideWeather= outsideWeather)
        uplink_message.payload_fields.timestamp = int(time.time())
        sensor = SENSOR_DEVID_LOCATION_DICT.get(uplink_message.dev_id)
        if sensor:
            locationName = sensor["locationName"]
            print("Data from SENSOR -> {}".format(uplink_message.dev_id))
            if locationName is None:
                print("Location name is getConstructedCustomerPathFromSubPathnone.")
                db.reference((NO_ZONE)).push(uplink_message.toJson())
            else:
                now = datetime.datetime.now()
                #print("ilk ifteyiz")
                todayAsString = "{:02d}-{:02d}-{}".format(now.day, now.month, now.year)
                #print("Today {}".format(todayAsString))
                db.reference(getConstructedCustomerPathFromSubPath(LOCATION_DATA)).child(locationName).push(uplink_message.payload_fields.toJson())
                #print("Pushed location: " + getConstructedCustomerPathFromSubPath(LOCATION_DATA).child(locationName))

                # constructedLocationPath = getSensorLocationPath(sensor)
                # #print("Constructed path -> {}".format(constructedLocationPath))
                #
                # print("Location name -> {}".format(locationName))
                # db.reference(getConstructedCustomerPathFromSubPath(LOCATION_PATH)).child(locationName).child("sensor").set(uplink_message.payload_fields.toJson())
                # db.reference(getConstructedCustomerPathFromSubPath(DASHNOARD_SENSORS_PATH)).child(uplink_message.dev_id).child(todayAsString).push(
                #     uplink_message.payload_fields.toJson())
                # db.reference(getConstructedCustomerPathFromSubPath(DASHNOARD_LOCATION_PATH)).child(locationName).child(todayAsString).push(
                #     uplink_message.payload_fields.toJson())
                # # ER Part
                # db.reference(getConstructedCustomerPathFromSubPath(ER_SENSORS)).child(locationName).child("lastSeen").set(uplink_message.payload_fields.toJson())
                # db.reference(getConstructedCustomerPathFromSubPath(ER_SENSORS)).child(locationName).child(todayAsString).push(
                #     uplink_message.payload_fields.toJson())
                print("Done writing firebase at {}".format(now))
                #locationSensorNotifyForEmpty(locationName, uplink_message.payload_fields)
    except Exception as e:
        print(e)
        print("Wrong payload length: {}".format(msgsize))
        isRetry = msg[5]
        uplink_message = UplinkMessage(msg, isRetry=True, outsideWeather= outsideWeather)
        uplink_message.payload_fields.timestamp = int(time.time())
        sensor = SENSOR_DEVID_LOCATION_DICT.get(uplink_message.dev_id)
        print("Data from SENSOR -> {}".format(uplink_message.dev_id))
        if sensor:
            locationName = sensor["locationName"]
            if locationName is None:
                print("Location name is none.")
                db.reference((NO_ZONE)).push(uplink_message.toJson())
            else:
                now = datetime.datetime.now()
                todayAsString = "{:02d}-{:02d}-{}".format(now.day, now.month, now.year)
                print("Today {}".format(todayAsString))
                db.reference(getConstructedCustomerPathFromSubPath(LOCATION_DATA)).child(locationName).push(uplink_message.payload_fields.toJson())
                constructedLocationPath = getSensorLocationPath(sensor)
                #print("Constructed path -> {}".format(constructedLocationPath))
                print("Location name -> {}".format(locationName))
                # db.reference(getConstructedCustomerPathFromSubPath(LOCATION_PATH)).child(locationName).child("sensor").set(uplink_message.payload_fields.toJson())
                # db.reference(getConstructedCustomerPathFromSubPath(DASHNOARD_SENSORS_PATH)).child(uplink_message.dev_id).child(todayAsString).push(
                #     uplink_message.payload_fields.toJson())
                #
                # db.reference(getConstructedCustomerPathFromSubPath(DASHNOARD_LOCATION_PATH)).child(locationName).child(todayAsString).push(
                #     uplink_message.payload_fields.toJson())
                #
                # # ER Part
                # db.reference(getConstructedCustomerPathFromSubPath(ER_SENSORS)).child(locationName).child("lastSeen").set(uplink_message.payload_fields.toJson())
                # db.reference(getConstructedCustomerPathFromSubPath(ER_SENSORS)).child(locationName).child(todayAsString).push(
                #     uplink_message.payload_fields.toJson())
                print("Done writing firebase at {}".format(now))
                #locationSensorNotifyForEmpty(locationName, uplink_message.payload_fields)


def downlink_callback(mid, client):
    print("Recieved downlink: ", mid)


def outside_data_handler():
    pass


def main():

    print("starting")

    client = MQTTClient(app_id, access_key, mqtt_address="", discovery_address="discovery.thethings.network:1900")
    client.set_connect_callback(connect_callback)
    client.set_downlink_callback(downlink_callback)
    client.set_uplink_callback(uplink_callback)

    client.connect()

    appClient = ApplicationClient(app_id, access_key, handler_address="", cert_content="",
                                  discovery_address="discovery.thethings.network:1900")
    app = appClient.get()
    devices = appClient.devices()


if __name__ == "__main__":
    main()
    print("going")
    k = input("press close to exit\n")
