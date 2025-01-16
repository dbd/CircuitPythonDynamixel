from dynamixel.protocol import Protocol2
from dynamixel.servo import Servo

class OperatingMode:
    OP_VELOCITY = 1
    OP_POSITION = 3
    OP_EXTENDED_POSITION = 4
    OP_PWM = 16


class ParamUnit:
    UNIT_RAW = 0
    UNIT_PERCENT = 1
    UNIT_RPM = 2
    UNIT_DEGREE = 3
    UNIT_MILLI_AMPERE = 4


class Message:
    UNDEF = 0
    BEGIN = 1
    GET_BAUD = 2
    PING = 3
    SCAN = 4
    SET_MODEL_NUMBER = 5
    GET_MODEL_NUMBER = 6
    SET_PROTOCOL = 7
    SET_BAUDRATE = 8
    TORQUE_ON = 9
    TORQUE_OFF = 10
    LED_ON = 11
    LED_OFF = 12
    SET_OPERATING_MODE = 13
    SET_GOAL_POSITION = 14
    GET_PRESENT_POSITION = 15
    SET_GOAL_VELOCITY = 16
    GET_PRESENT_VELOCITY = 17
    SET_GOAL_PWM = 18
    GET_PRESENT_PWM = 19
    SET_GOAL_CURRENT = 20
    GET_PRESENT_CURRENT = 21
    GET_TORQUE_ENABLED_STAT = 22
    READ_CONTROL_TABLE_ITEM = 23
    WRITE_CONTROL_TABLE_ITEM = 24
    CONTROL_SET_PROTOCOL_VERSION = 25


class CONTROL_TABLE:
    MODEL_NUMBER = (0, 2)
    MODEL_INFORMATION = (2, 4)
    FIRMWARE_VERSION = (6, 1)
    ID = (7, 1)
    BAUD = (8, 1)
    RETURN_DELAY_TIME = (9, 1)
    DRIVE_MODE = (10, 1)
    OPERATING_MODE = (11, 1)
    SECONDARY_SHADO = (12, 1)
    PROTOCOL_TYPE = (13, 1)
    HOMING_OFFSET = (20, 4)
    MOVING_THRESHOLD = (24, 4)
    TEMPERATURE_LIMIT = (31, 1)
    MAX_VOLTAGE_LIMIT = (32, 2)
    MIN_VOLTAGE_LIMIT = (34, 2)
    PWM_LIMIT = (36, 2)
    VELOCITY_LIMIT = (44, 4)
    MAX_POSITION_LIMIT = (48, 4)
    MIN_POSITION_LIMIT = (52, 4)
    STARTUP_CONFIGURATION = (60, 1)
    SHUTDOWN = (63, 1)
    TORQUE_ENABLE = (64, 	1)
    LED = (65, 	1)
    STATUS_RETURN_LEVEL = (68, 1)
    REGISTERED_INSTRUCTION = (69, 1)
    HARDWARE_ERROR_STATUS = (70, 1)
    VELOCITY_I_GAIN = (76, 2)
    VELOCITY_P_GAIN = (78, 2)
    POSITION_D_GAIN = (80, 2)
    POSITION_I_GAIN = (82, 2)
    POSITION_P_GAIN = (84, 2)
    FEEDFORWARD_2ND_GAIN = (88, 2)
    FEEDFORWARD_1ST_GAIN = (90, 2)
    BUS_WATCHDOG = (98, 1)
    GOAL_PWM = (100, 2)
    GOAL_VELOCITY = (104, 4)
    PROFILE_ACCELERATION = (108, 4)
    PROFILE_VELOCITY = (112, 4)
    GOAL_POSITION = (116, 4)
    REALTIME_TICK = (120, 2)
    MOVING = (122, 1)
    MOVING_STATUS = (123, 1)
    PRESENT_PWM = (124, 2)
    PRESENT_LOAD = (126, 2)
    PRESENT_VELOCITY = (128, 4)
    PRESENT_POSITION = (132, 4)
    VELOCITY_TRAJECTORY = (136, 4)
    POSITION_TRAJECTORY = (140, 4)
    PRESENT_INPUT_VOLTAGE = (144, 2)
    PRESENT_TEMPERATURE = (146, 1)
    BACKUP_READY = (147, 1)


class XL430_W250_T(Servo):
    def __init__(self, *args, unit=ParamUnit.UNIT_DEGREE, **kwargs):
        super(XL430_W250_T, self).__init__(*args, **kwargs)
        self.unit = unit
        self.protocol = Protocol2()

    def setProtocolVersion(self, protocol):
        return self.write(Message.SET_PROTOCOL, protocol)

    def ping(self):
        res = self.protocol.ping(self.id)
        return res
    
    def torqueOn(self):
        return self.write(Message.TORQUE_ON)

    def torqueOff(self):
        return self.write(Message.TORQUE_OFF)

    def getBaud(self):
        return self.write(Message.GET_BAUD)

    def scan(self):
        return self.write(Message.SCAN)

    def setModelNumber(self):
        return self.write(Message.SET_MODEL_NUMBER)

    def getModelNumber(self):
        return self.write(Message.GET_MODEL_NUMBER)

    def setProtocol(self):
        return self.write(Message.SET_PROTOCOL)

    def setBaudrate(self):
        return self.write(Message.SET_BAUDRATE)

    def ledOn(self):
        res = self.write(CONTROL_TABLE.LED, 1)
        if res != 'OK':
            return res

    def ledOff(self):
        res = self.write(CONTROL_TABLE.LED, 0)
        if res != 'OK':
            return res

    def setOperationMode(self, operatingMode):
        res = self.write(Message.SET_OPERATING_MODE, operatingMode)
        return res

    def setGoalPosition(self, value, unit=None):
        unit = unit or self.unit
        return self.write(Message.SET_GOAL_POSITION, value, unit)

    def setPreciseGoalPosition(self, value, unit=None):
        unit = unit or self.unit
        self.setGoalPosition(value, unit=unit)
        tries = 0
        while self.getPresentPosition(unit=unit) != value:
            self.setGoalPosition(value+11, unit=unit)
            self.setGoalPosition(value, unit=unit)
            if tries >= 3:
                print('failed to set precise position')
                break
            tries += 1

        return self.write(Message.SET_GOAL_POSITION, value, unit)

    def getPresentPosition(self, unit=None):
        unit = unit or self.unit
        msg = self.write(Message.GET_PRESENT_POSITION, unit)
        if msg == 'undef':
            return 'error'
        self.position = int(msg.split('.')[0])
        return self.position

    def setGoalVelocity(self, value, unit=None):
        unit = unit or self.unit
        return self.write(Message.SET_GOAL_VELOCITY, value, unit)

    def getPresentVelocity(self, unit=None):
        unit = unit or self.unit
        return self.write(Message.GET_PRESENT_VELOCITY, unit)

    def setGoalPwm(self, value, unit=None):
        unit = unit or self.unit
        return self.write(Message.SET_GOAL_PWM, value, unit)

    def getPresentPwm(self, unit=None):
        unit = unit or self.unit
        return self.write(Message.GET_PRESENT_PWM, unit)

    def setGoalCurrent(self, unit=None):
        unit = unit or self.unit
        return self.write(Message.SET_GOAL_CURRENT)

    def getPresentCurrent(self, unit=None):
        unit = unit or self.unit
        return self.write(Message.GET_PRESENT_CURRENT)

    def getTorqueEnabledStat(self, unit=None):
        unit = unit or self.unit
        return self.write(Message.GET_TORQUE_ENABLED_STAT)

    def readControlTableItem(self, item):
        if not isinstance(item, tuple):
            return f"readControlTableItem takes a tuple, got {item}"
        idx = item[0]
        size = item[1]
        return self.write(Message.READ_CONTROL_TABLE_ITEM, idx, size)

    def writeControlTableItem(self, item, data):
        if not isinstance(item, tuple):
            return f"writeControlTableItem takes a tuple, got {item}"
        idx = item[0]
        size = item[1]
        return self.write(Message.WRITE_CONTROL_TABLE_ITEM, idx, size, data)
