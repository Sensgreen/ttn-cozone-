from default.MessageMetadata import MessageMetadata
from default.MessagePayload import MessagePayload


class UplinkMessage:
    def __init__(self, msg, isRetry= False, outsideWeather= {'temp': -1, 'humidity': -1}):
        if isRetry == False:
            self.app_id = msg[0]
            self.dev_id = msg[1]
            self.hardware_serial = msg[2]
            self.port = msg[3]
            self.counter = msg[4]
            self.confirmed = msg[5]
            self.payload_raw = msg[6]
            self.payload_fields = MessagePayload(msg[7],outsideWeather)
            self.metadata = MessageMetadata(msg[8])
        else:
            self.app_id = msg[0]
            self.dev_id = msg[1]
            self.hardware_serial = msg[2]
            self.port = msg[3]
            self.counter = msg[4]
            self.confirmed = msg[6]
            self.payload_raw = msg[7]
            self.payload_fields = MessagePayload(msg[8], outsideWeather)
            self.metadata = MessageMetadata(msg[9])

    def toJson(self):
        return dict(app_id=self.app_id, dev_id=self.dev_id, hardware_serial=self.hardware_serial, port=self.port,
                    counter=self.counter, payload_raw=self.payload_raw, payload_fields=self.payload_fields.toJson(),
                    metadata=self.metadata.toJson())
