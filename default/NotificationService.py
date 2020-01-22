# Send to single device.
import datetime

from firebase_admin import db
from pyfcm import FCMNotification

USERS_PATH = "sensme/users/"
NOTIFICATION_PATH = "notification"

location_presence_map = {}


def isWorkTime():
    now_time = datetime.datetime.utcnow()  # utc comes 3 hours early from Turkey's time
    weekday = now_time.weekday()
    if weekday == 6 or weekday == 5:
        # Sunday or Saturday, dismiss
        return False
    if now_time.hour >= 6 and now_time.hour <= 16:  # 09:00:00 - 19:59:59 in turkey
        return True
    else:
        return False


def sendNotification(registerId, locationName, messagePayload):
    # REGISTER_ID_NOTE3 = "dTzQk6Qwa68:APA91bHlH00ziMgAqm49EzKAUq1rNjJ2o8_qgmUzlqyWudRoG5yyDzSOVnOiWqOtuOuA-PGDZHyEpUP_ka2dkUids8znt5tzOBIr0uDB7STXv6XjjCSypcgi1wgH090slwwZZXQzmW92"
    API_KEY = "AAAAmGB_srs:APA91bEtDWOmf73VSWrptEKxmHkR6CNUWyFcJKr1CgUBvXPu1moi-NlY9W_r26Ahs8SVPA5PtUkOMtouUVKlqqjP0J9-tLrEiIu60QBcXxr8iZHYDvJiwmKhL2iQPNsrqKv389Irifmp"
    push_service = FCMNotification(api_key=API_KEY)
    message_title = "Available Room"
    message_body = "Room " + locationName + " is empty now!"
    result = push_service.notify_single_device(registration_id=registerId, message_title=message_title,
                                               message_body=message_body)

    print(result)


def locationSensorNotifyForEmpty(locationName, messagePayload):
    print(location_presence_map)
    if isWorkTime():
        if locationName is None:
            return
        else:
            if messagePayload.presence == 0:
                oldValue = location_presence_map.get(locationName)
                if oldValue is None:
                    location_presence_map[locationName] = 0
                else:
                    location_presence_map[locationName] = oldValue + 1
            else:
                location_presence_map[locationName] = None
            users = db.reference(USERS_PATH).get()
            if users is not None:
                for key, value in users.items():
                    isNotifiable = db.reference(USERS_PATH).child(key).child(NOTIFICATION_PATH).child(
                        locationName).get()
                    if isNotifiable is not None:
                        registerId = isNotifiable
                        emptyCount = location_presence_map[locationName]
                        if emptyCount is not None:
                            if emptyCount > 3: # if 4 or more consecutive empty message is sent send notification
                                sendNotification(registerId, locationName, messagePayload)
                                location_presence_map[locationName] = None
    else:
        return
