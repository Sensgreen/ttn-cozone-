import time


class MessagePayload:
    def __init__(self, payload_fields, outsideWeather):
        self.humidity = payload_fields[0]
        self.temp_int = payload_fields[1]
        self.temp_dec= payload_fields[2]
        self.presence = payload_fields[3]
        self.timestamp = int(time.time())
        self.carbonDioxide = -1
        self.outsideTemperature = outsideWeather['temp']
        self.outsideHumidity = outsideWeather['humidity']
        self.temperature= self.temp_int+self.temp_dec

    def toJson(self):
        return dict(humidity=self.humidity, presence=self.presence, temperature=self.temperature,
                    outsideTemperature=self.outsideTemperature, outsideHumidity=self.outsideHumidity,
                    timestamp=self.timestamp, carbonDioxide=self.carbonDioxide)
