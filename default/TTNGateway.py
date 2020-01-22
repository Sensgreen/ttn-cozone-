class TTNGateway:
    def __init__(self, gateway):
        self.gtw_id = gateway[0]
        self.timestamp = gateway[1]
        self.time = gateway[2]
        self.channel = gateway[3]
        self.rssi = gateway[4]
        self.snr = gateway[5]
        self.rf_chain = gateway[6]
        self.latitude = gateway[7]
        self.longitude = gateway[8]

    def toJson(self):
        return dict(gtw_id=self.gtw_id, timestamp=self.timestamp, time=self.time, channel=self.channel,
                    rssi=self.rssi, snr=self.snr, rf_chain=self.rf_chain,
                    latitude=self.latitude, longitude=self.longitude)
