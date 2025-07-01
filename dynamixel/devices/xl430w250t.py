from dynamixel.protocol import Protocol2
from dynamixel.servo import Servo, paramUnit
import asyncio


class operatingMode:
    OP_VELOCITY = 1
    OP_POSITION = 3
    OP_EXTENDED_POSITION = 4
    OP_PWM = 16


class controlTable:
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
    TORQUE_ENABLE = (64, 1)
    LED = (65, 1)
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
    CONTROL_TABLE = controlTable
    PARAM_UNIT = paramUnit
    OPERATING_MODE = operatingMode

    def __init__(self, *args, unit=PARAM_UNIT.UNIT_DEGREE, **kwargs):
        super(XL430_W250_T, self).__init__(*args, **kwargs)
        self.unit = unit
        self.protocol = Protocol2(**kwargs)
        self.resolution = 4096
        self.negative = False
        self.torqueEnabled = False
        self.moving = False

    async def run(self):
        while True:
            self.getPresentPosition()

            self.moving = bool(self.readControlTableItem(self.CONTROL_TABLE.MOVING))
            self.torqueEnabled = bool(self.readControlTableItem(self.CONTROL_TABLE.TORQUE_ENABLE))
            await asyncio.sleep(.1)

    def clear(self):
        self.protocol.reboot(self.id)

    def setProtocolVersion(self, protocol):
        return self.write(Message.SET_PROTOCOL, protocol)

    def ping(self):
        res = self.protocol.ping(self.id)
        return res

    def torqueOn(self):
        res = self.writeControlTableItem(self.CONTROL_TABLE.TORQUE_ENABLE, 1)
        if res != "OK":
            return res

    def torqueOff(self):
        res = self.writeControlTableItem(self.CONTROL_TABLE.TORQUE_ENABLE, 0)
        if res != "OK":
            return res

    def getBaud(self):
        res = self.readControlTableItem(self.CONTROL_TABLE.BAUD)
        return res

    def getModelNumber(self):
        res = self.readControlTableItem(self.CONTROL_TABLE.BAUD)
        return res

    def setBaudrate(self, value):
        res = self.writeControlTableItem(self.CONTROL_TABLE.BAUD, value)
        if res != "OK":
            return res

    def ledOn(self):
        res = self.writeControlTableItem(self.CONTROL_TABLE.LED, 1)
        if res != "OK":
            return res

    def ledOff(self):
        res = self.writeControlTableItem(self.CONTROL_TABLE.LED, 0)
        if res != "OK":
            return res

    def setOperationMode(self, operatingMode):
        res = self.writeControlTableItem(
            self.CONTROL_TABLE.OPERATING_MODE, operatingMode
        )
        if res != "OK":
            return res


    def convertNegative(self, value, length):
        """Compute the 2's complement of int value val"""
        maxInt = int.from_bytes(bytes([0xFF]*length), 'little')
        if value < 0:
            maxInt += value
            return list(maxInt.to_bytes(length, 'little'))
        else:
            res = maxInt - value
            return res

    def setGoalPosition(self, value, unit=None):
        # Need to do a unit conversion
        unit = unit or self.unit
        value = self.convertUnits(value, unit)
        if value < 0:
            self.negative = True
            value = self.convertNegative(value, self.CONTROL_TABLE.GOAL_POSITION[1])
        else:
            self.negative = False
        res = self.writeControlTableItem(self.CONTROL_TABLE.GOAL_POSITION, value)
        if res != "OK":
            return res

    def getPresentPosition(self, unit=None):
        unit = unit or self.unit
        res = self.readControlTableItem(self.CONTROL_TABLE.PRESENT_POSITION)
        if isinstance(res, int):
            if self.negative:
                res = self.convertNegative(res, self.CONTROL_TABLE.GOAL_POSITION[1])
            res = self.convertRaw(res, unit)
            if self.negative:
                res *= -1
            self.position = res
        return self.position

    def setMaxPosition(self, value, unit=None):
        unit = unit or self.unit
        value = self.convertUnits(value, unit)
        res = self.writeControlTableItem(self.CONTROL_TABLE.MAX_POSITION_LIMIT, value)
        if res != "OK":
            return res

    def setMinPosition(self, value, unit=None):
        unit = unit or self.unit
        value = self.convertUnits(value, unit)
        res = self.writeControlTableItem(self.CONTROL_TABLE.MIN_POSITION_LIMIT, value)
        if res != "OK":
            return res

    def getPositionLimits(self, unit=None):
        unit = unit or self.unit
        maxRes = self.readControlTableItem(self.CONTROL_TABLE.MAX_POSITION_LIMIT)
        minRes = self.readControlTableItem(self.CONTROL_TABLE.MIN_POSITION_LIMIT)
        if isinstance(maxRes, int):
            maxRes = self.convertRaw(maxRes, unit)
        if isinstance(minRes, int):
            minRes = self.convertRaw(minRes, unit)
        return (minRes, maxRes)

    def setGoalVelocity(self, value):
        res = self.writeControlTableItem(self.CONTROL_TABLE.GOAL_VELOCITY, value)
        if res != "OK":
            return res

    def getPresentVelocity(self):
        res = self.readControlTableItem(self.CONTROL_TABLE.PRESENT_VELOCITY)
        return res

    def setGoalPwm(self, value):
        res = self.writeControlTableItem(self.CONTROL_TABLE.GOAL_PWM, value)
        if res != "OK":
            return res

    def getPresentPwm(self):
        res = self.readControlTableItem(self.CONTROL_TABLE.PRESENT_PWM)
        return res

    def getTorqueEnabled(self):
        res = self.readControlTableItem(self.CONTROL_TABLE.TORQUE_ENABLE)
        return res
