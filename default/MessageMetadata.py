from default.TTNGateway import TTNGateway


class MessageMetadata:
    def __init__(self, metadata):
        self.time = metadata[0]
        self.frequency = metadata[1]
        self.modulation = metadata[2]
        self.data_rate = metadata[3]
        self.airtime = metadata[4]
        self.coding_rate = metadata[5]
        gtws = metadata[6]
        self.gateways = TTNGateway(metadata[6][0])

    def toJson(self):
        return dict(time=self.time, frequency=self.frequency, modulation=self.modulation, data_rate=self.data_rate,
                    airtime=self.airtime, coding_rate=self.coding_rate, gateways=self.gateways.toJson())
