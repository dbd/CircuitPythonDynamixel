class Servo:
    def __init__(self, name, servo_id, **kwargs):
        self.name = name
        self.id = servo_id
        self.torque = False
        self.position = None
        self.initial_position = None
        self.protocol = None

    def write(self, message, *args):
        return self.protocol.write(self.id, *message, *args)

    def ping(self):
        assert False, "Not implemented"

    def torqueOn(self):
        assert False, "Not implemented"

    def torqueOff(self):
        assert False, "Not implemented"

    def getBaud(self):
        assert False, "Not implemented"

    def scan(self):
        assert False, "Not implemented"

    def setModelNumber(self):
        assert False, "Not implemented"

    def getModelNumber(self):
        assert False, "Not implemented"

    def setProtocol(self):
        assert False, "Not implemented"

    def setBaudrate(self):
        assert False, "Not implemented"

    def ledOn(self):
        assert False, "Not implemented"

    def ledOff(self):
        assert False, "Not implemented"

    def setOperationMode(self, operatingMode):
        assert False, "Not implemented"

    def setGoalPosition(self, value, unit=None):
        assert False, "Not implemented"

    def setPreciseGoalPosition(self, value, unit=None):
        assert False, "Not implemented"

    def getPresentPosition(self, unit=None):
        assert False, "Not implemented"

    def setGoalVelocity(self, value, unit=None):
        assert False, "Not implemented"

    def getPresentVelocity(self, unit=None):
        assert False, "Not implemented"

    def setGoalPwm(self, value, unit=None):
        assert False, "Not implemented"

    def getPresentPwm(self, unit=None):
        assert False, "Not implemented"

    def setGoalCurrent(self, unit=None):
        assert False, "Not implemented"

    def getPresentCurrent(self, unit=None):
        assert False, "Not implemented"

    def getTorqueEnabledStat(self, unit=None):
        assert False, "Not implemented"

    def readControlTableItem(self, item):
        assert False, "Not implemented"

    def writeControlTableItem(self, item, data):
        assert False, "Not implemented"
