class paramUnit:
    UNIT_RAW = 0
    UNIT_PERCENT = 1
    UNIT_RPM = 2
    UNIT_DEGREE = 3
    UNIT_MILLI_AMPERE = 4


class Servo:
    def __init__(self, name, servo_id, **kwargs):
        self.name = name
        self.id = servo_id
        self.torque = False
        self.position = None
        self.initial_position = None
        self.protocol = None
        self.resolution = None
        self.moving = False

    def convertUnits(self, raw, unit):
        unitMap = {
            paramUnit.UNIT_DEGREE: lambda raw: int((raw / 360) * self.resolution)
        }
        return unitMap.get(unit, lambda raw: raw)(raw)

    def convertRaw(self, raw, unit):
        unitMap = {
            paramUnit.UNIT_DEGREE: lambda raw: int((raw / self.resolution) * 360)
        }
        return unitMap.get(unit, lambda raw: raw)(raw)

    def read(self, addr, length):
        return self.protocol.read(self.id, addr, length)

    def write(self, message, *args):
        return self.protocol.write(self.id, *message, *args)

    def reboot(self):
        self.protocol.reboot(self.id)

    def clear(self, position=False, error=False):
        if self.protocol.VERSION == "2.0":
            self.protocol.clear(self.id, position=position, error=error)
        else:
            return "Not supported on Protocol v1.0"

    def ping(self):
        assert False, "Not implemented"

    def torqueOn(self):
        assert False, "Not implemented"

    def torqueOff(self):
        assert False, "Not implemented"

    def getBaud(self):
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
        unit = unit or self.unit
        self.setGoalPosition(value, unit=unit)
        tries = 0
        while self.getPresentPosition(unit=unit) != value:
            self.setGoalPosition(value + 11, unit=unit)
            self.setGoalPosition(value, unit=unit)
            if tries >= 3:
                print("failed to set precise position")
                break
            tries += 1

        return self.write(Message.SET_GOAL_POSITION, value, unit)

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
        if not isinstance(item, tuple):
            return f"readControlTableItem takes a tuple, got {item}"
        return self.read(*item)

    def writeControlTableItem(self, item, data):
        if not isinstance(item, tuple):
            return f"writeControlTableItem takes a tuple, got {item}"
        return self.write(item, data)
