import digitalio
import time
import busio
import board
from .utils import Lock



class Protocol:
    BROADCAST = 254
    ERR_RX_CRC_MISMATCH = "ERR_RX_CRC_MISMATCH"
    ERR_RX_FAILED_TO_RX_ENTIRE_PACKET = "ERR_RX_FAILED_TO_RX_ENTIRE_PACKET"
    ERR_RX_NO_RESPONSE = "ERR_RX_NO_RESPONSE"

    ERR_RESULT_FAIL = "ERR_RESULT_FAIL"
    ERR_INSTR_ERROR = "ERR_RESULT_FAIL"
    ERR_CRC_ERR = "ERR_RESULT_FAIL"
    ERR_DATA_RANGE_ERROR = "ERR_RESULT_FAIL"
    ERR_DATA_LENGTH_ERROR = "ERR_RESULT_FAIL"
    ERR_DATA_LIMIT_ERROR = "ERR_RESULT_FAIL"
    ERR_ACCESS_ERROR = "ERR_RESULT_FAIL"

    OK = 'OK'

    def __init__(self, tx_enable=board.D2, baudRate=1000000, tx=board.RX, rx=board.TX, timeout=1):
        self.uart = busio.UART(tx, rx, baudrate=baudRate, timeout=timeout)
        lock = Lock()
        self.lock = lock
        self.tx_enable = digitalio.DigitalInOut(tx_enable)
        self.tx_enable.direction = digitalio.Direction.OUTPUT
        self.tx_enable.value = True


class Protocol1(Protocol):
    # (LEN, INST)
    INSTR_PING = 0x01
    INSTR_READ = 0x02
    INSTR_WRITE = 0x03
    INSTR_REG_WRITE = 0x04
    INSTR_ACTION = 0x05
    INSTR_FACTORY_RESET = 0x06
    INSTR_REBOOT = 0x08
    INSTR_SYNC_WRITE = 0x83
    INSTR_BULK_READ = 0x92

    def __init__(self):
        super(Protocol1, self).__init__()

    def checksum(packet):
        pass


class Protocol2(Protocol):
    _instance = None
    initialized = False

    INSTR_PING = 0x01
    INSTR_READ = 0x02
    INSTR_WRITE = 0x03
    INSTR_REG_WRITE = 0x04
    INSTR_ACTION = 0x05
    INSTR_FACTORY_RESET = 0x06
    INSTR_REBOOT = 0x08
    INSTR_CLEAR = 0x10
    INSTR_CONTROL_TABLE_BACKUP = 0x20
    INSTR_SYNC_READ = 0x82
    INSTR_SYNC_WRITE = 0x83
    INSTR_FAST_SYNC_READ = 0x8A
    INSTR_BULK_READ = 0x92
    INSTR_BULK_WRITE = 0x93
    INSTR_FAST_BULK_READ = 0x9A

    # INSTR Packet
    class Packet:
        HEADER = [0, 1, 2]
        RESERVED = [4]
        ID = [5]
        LENGTH = [6, 7]
        INSTR = [8]
        CRC = [-2, -1]

    # HEADER ID LENGTH INSTR PARAM CRC

    # STATUS Packet
    # HEADER ID LENGTH INSTR ERR PARAM CRC

    HEADERS = [0xFF, 0xFF, 0xFD]
    RESERVED = [0x00]
    LENGTH_PLACEHOLDER = [0x00, 0x00]
    LENGTH_INDICES = (5, 6)

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Protocol2, cls).__new__(cls)
        return cls._instance

    def __init__(self, *args, **kwargs):
        if not self.initialized:
            super(Protocol2, self).__init__(*args, **kwargs)
        self.initialized = True
        self.STATUS_ERRORS = [
            None,
            self.ERR_RESULT_FAIL,
            self.ERR_INSTR_ERROR,
            self.ERR_CRC_ERR,
            self.ERR_DATA_RANGE_ERROR,
            self.ERR_DATA_LENGTH_ERROR,
            self.ERR_DATA_LIMIT_ERROR,
            self.ERR_ACCESS_ERROR,
        ]

    def checksum(self, packet):
        crc_accum = 0
        crc_table = []
        polynomial = 0x8005  # CRC-16-ANSI (x^16 + x^15 + x^2 + 1)

        for i in range(256):
            crc = (
                i << 8
            )  # Start with the value of the byte shifted to the left by 8 bits
            for j in range(8):  # For each bit in the byte
                if crc & 0x8000:  # If the highest bit is set
                    crc = (
                        crc << 1
                    ) ^ polynomial  # Shift left and XOR with the polynomial
                else:
                    crc <<= 1  # Just shift left
                crc &= 0xFFFF  # Ensure we keep it within 16 bits
            crc_table.append(crc)

        for j in range(0, len(packet) - 2):
            i = ((crc_accum >> 8) ^ packet[j]) & 0xFF
            crc_accum = ((crc_accum << 8) ^ crc_table[i]) & 0xFFFF
        return list(crc_accum.to_bytes(2, "little"))

    def packetLength(self, packet):
        # Length is the instruction + params + CRC
        # simplified to num params + 3
        pl = len(packet)
        return list(pl.to_bytes(2, "little"))

    def addStuffing(self, packet):
        padIndices = []
        for i in range(len(packet)):
            j = packet[i : i + 4]
            if len(j) == 4 and j[:3] == self.HEADERS and j[3] != 0xFD:
                padIndices.append(i + 3 + len(padIndices))
            elif len(j) == 3 and j == self.HEADERS:
                padIndices.append(i + 3 + len(padIndices))
        for padIndex in padIndices:
            packet.insert(padIndex, 0xFD)
        return packet

    def updateLength(self, packet):
        pl = self.packetLength(packet[7:] + [0x00, 0x00])
        for index, value in zip(self.Packet.LENGTH, pl):
            packet[index - 1] = value
        return packet

    def addHeaders(self, packet):
        return self.HEADERS + self.RESERVED + packet

    def addChecksum(self, packet):
        return packet + self.checksum(packet + [0x00, 0x00])

    def send(self, packet):
        """Transmission Process

        1. Generate basic packet structure including required parameters.
        2. Apply Byte Stuffing to ensure that packets are processed successfully.
        3. Update packet length to include any stuffed bytes.
        4. Calculate final CRC with byte stuffing applied.
        """
        packet = self.addStuffing(packet)
        packet = self.addHeaders(packet)
        packet = self.updateLength(packet)
        packet = self.addChecksum(packet)
        # Packet at this point matches the official sdk
        res = 'ERR'
        with self.lock:
            self.tx_enable.value = True
            time.sleep(0.01)
            self.uart.write(bytes(packet))
            self.tx_enable.value = False
            time.sleep(0.01)
            res = self.receive()
            self.uart.reset_input_buffer()
        return res

    def receive(self):
        def validationErrors(packet):
            crc = self.checksum(packet[:-2] + [0x00, 0x00])
            if crc != packet[-2:]:
                return self.ERR_RX_CRC_MISMATCH
            err = packet[8]
            if err:
                return self.STATUS_ERRORS[err]
            return None
        length = 0
        # read in HEADER HEADER HEADER RESERVED ID LENGTH_LOW LENGTH_HIGH 55 ERR CRC_LOW CRC_HIGH
        packet = self.uart.read(self.uart.in_waiting)

        # uncomment the following to see the actual hex, the status packet instr is 55 
        # but will show up in list(packet) as 85 which is just confusing. You can also
        # capture the send and receive in the dynamixel wizard if you plug on cable into
        # a u2d2 and select View > Packet
        # tp = [f'0x{i:02X}'for i in packet]
        # print(f'raw response: {tp}')

        if packet is None:
            return "RX_TIMEOUT"
        else:
            packet = list(packet)
        if packet[:3] == self.HEADERS:
            low, high = packet[5 : 6 + 1]
            length = int.from_bytes(bytes([low, high]), "little")
            if length + 7 == len(packet):
                return validationErrors(packet) or packet
            else:
                toRead = 11-(length + 1) # plus one because length include the instruction
                t = self.uart.read(toRead)
                if t is None:
                    return self.ERR_RX_FAILED_TO_RX_ENTIRE_PACKET
                packet += list(t)
                if self.uart.in_waiting:
                    t = self.uart.read(self.uart.in_waiting)
                packet += list(t)
                return validationErrors(packet) or packet
        for i in range(len(packet)):
            j = packet[i : i + 4]
            if len(j) == 4 and j[:3] == self.HEADERS and j[3] != 0xFD:
                break
        else:
            if not self.uart.in_waiting:
                return self.ERR_RX_NO_RESPONSE
            packet = list(self.uart.read(self.uart.in_waiting))
        if packet:
            return validationErrors(packet) or packet

        return self.ERR_RX_ERROR

    def ping(self, ID):
        length = self.packetLength([self.INSTR_PING, 0x00, 0x00])
        packet = [ID] + length + [self.INSTR_PING]
        return self.send(packet)

    def read(self, ID, addr, length):
        addrLowHigh = list(addr.to_bytes(2, "little"))
        lengthLowHigh = list(length.to_bytes(2, "little"))
        pl = self.packetLength(
            [self.INSTR_READ] + addrLowHigh + lengthLowHigh + [0x00, 0x00]
        )
        packet = [ID] + pl + [self.INSTR_READ] + addrLowHigh + lengthLowHigh
        res = self.send(packet)
        if res is None or isinstance(res, str):
            return res
        data = int.from_bytes(bytes(res[9:-2]), 'little')
        return data

    def write(self, ID, addr, length, data):
        addrLowHigh = list(addr.to_bytes(2, "little"))
        dataLowHigh = list(data.to_bytes(length, "little"))
        pl = self.packetLength(
            [self.INSTR_WRITE] + addrLowHigh + dataLowHigh + [0x00, 0x00]
        )
        packet = [ID] + pl + [self.INSTR_WRITE] + addrLowHigh + dataLowHigh
        return self.send(packet)

    def regWrite(self, ID, addr, length, data):
        addrLowHigh = list(addr.to_bytes(2, "little"))
        dataLowHigh = list(data.to_bytes(length, "little"))
        pl = self.packetLength(
            [self.INSTR_REG_WRITE] + addrLowHigh + dataLowHigh + [0x00, 0x00]
        )
        packet = [ID] + pl + [self.INSTR_REG_WRITE] + addrLowHigh + dataLowHigh
        return self.send(packet)

    def action(self, ID):
        length = self.packetLength([self.INSTR_ACTION, 0x00, 0x00])
        packet = [ID] + length + [self.INSTR_ACTION]
        return self.send(packet)

    def factoryReset(
        self, ID, resetAll=False, resetAllExceptId=False, resetAllExceptIdBaud=False
    ):
        p = 0x00
        if resetAll:
            p = 0xFF
        elif resetAllExceptId:
            p = 0x01
        elif resetAllExceptIdBaud:
            p = 0x02
        else:
            return 0
        length = self.packetLength([self.INSTR_FACTORY_RESET, p, 0x00, 0x00])
        packet = [ID] + length + [self.INSTR_FACTORY_RESET, p]
        res = self.send(packet)

    def reboot(self, ID):
        length = self.packetLength([self.INSTR_REBOOT, 0x00, 0x00])
        packet = [ID] + length + [self.INSTR_REBOOT]
        return self.send(packet)

    def clear(self, ID, position=False, error=False):
        p = 0x00
        if position:
            p = 0x01
            d = [0x44, 0x58, 0x4C, 0x22]
        elif error:
            p = 0x02
            d = [0x45, 0x52, 0x43, 0x4C]
        else:
            return 0
        pl = self.packetLength([self.INSTR_CLEAR, p] + d + [0x00, 0x00])
        packet = [ID] + pl + [self.INSTR_CLEAR, p] + d
        return self.send(packet)

    def controlTableBackup(self, ID, store=False, restore=False):
        p = 0x00
        if store:
            p = [0x01, 0x43, 0x54, 0x52, 0x4C]
        elif restore:
            p = [0x02, 0x43, 0x54, 0x52, 0x4C]
        else:
            return 0
        pl = self.packetLength([self.INSTR_CONTROL_TABLE_BACKUP] + p + [0x00, 0x00])
        packet = [ID] + pl + [self.INSTR_CONTROL_TABLE_BACKUP] + p
        return self.send(packet)

    def syncRead(self, addr, length, ids):
        p = []
        addrLowHigh = list(addr.to_bytes(2, "little"))
        lengthLowHigh = list(length.to_bytes(2, "little"))
        pl = self.packetLength(
            [self.INSTR_SYNC_READ] + addrLowHigh + lengthLowHigh + ids + [0x00, 0x00]
        )
        packet = (
            [self.BROADCAST]
            + pl
            + [self.INSTR_SYNC_READ]
            + addrLowHigh
            + lengthLowHigh
            + ids
        )
        return self.send(packet)

    def syncWrite(self, addr, length, values):
        """
        Example call: p.syncWrite(116, 4, [(1, 150), (2, 170)])
        set value at 116 which is 4 bytes to 150 for motor 1 and 170 to motor 2
        """
        p = []
        for ID, value in values:
            p.append(ID)
            p.extend(list(value.to_bytes(length, "little")))
        addrLowHigh = list(addr.to_bytes(2, "little"))
        lengthLowHigh = list(length.to_bytes(2, "little"))
        pl = self.packetLength(
            [self.INSTR_SYNC_WRITE] + addrLowHigh + lengthLowHigh + p + [0x00, 0x00]
        )
        packet = (
            [self.BROADCAST]
            + pl
            + [self.INSTR_SYNC_WRITE]
            + addrLowHigh
            + lengthLowHigh
            + p
        )
        return self.send(packet)

    def fastSyncRead(self, addr, length, ids):
        addrLowHigh = list(addr.to_bytes(2, "little"))
        lengthLowHigh = list(length.to_bytes(2, "little"))
        pl = self.packetLength(
            [self.INSTR_FAST_SYNC_READ]
            + addrLowHigh
            + lengthLowHigh
            + ids
            + [0x00, 0x00]
        )
        packet = (
            [self.BROADCAST]
            + pl
            + [self.INSTR_FAST_SYNC_READ]
            + addrLowHigh
            + lengthLowHigh
            + ids
        )
        return self.send(packet)

    def bulkRead(self, values):
        """
        Example call: p.bulkRead(116, 4, [(1, 150), (2, 170)])
        set value at 116 which is 4 bytes to 150 for motor 1 and 170 to motor 2
        """
        p = []
        for ID, addr, length in values:
            p.append(ID)
            p.extend(list(addr.to_bytes(2, "little")))
            p.extend(list(length.to_bytes(2, "little")))
        pl = self.packetLength([self.INSTR_BULK_READ] + p + [0x00, 0x00])
        packet = [self.BROADCAST] + pl + [self.INSTR_BULK_READ] + p
        return self.send(packet)

    def bulkWrite(self, values):
        p = []
        for ID, addr, length, data in values:
            p.append(ID)
            p.extend(list(addr.to_bytes(2, "little")))
            p.extend(list(length.to_bytes(2, "little")))
            p.extend(list(data.to_bytes(length, "little")))
        pl = self.packetLength([self.INSTR_BULK_WRITE] + p + [0x00, 0x00])
        packet = [self.BROADCAST] + pl + [self.INSTR_BULK_WRITE] + p
        return self.send(packet)

    def fastBulkRead(self, values):
        """
        Example call: p.bulkRead(116, 4, [(1, 150), (2, 170)])
        set value at 116 which is 4 bytes to 150 for motor 1 and 170 to motor 2
        """
        p = []
        for ID, addr, length in values:
            p.append(ID)
            p.extend(list(addr.to_bytes(2, "little")))
            p.extend(list(length.to_bytes(2, "little")))
        pl = self.packetLength([self.INSTR_FAST_BULK_READ] + p + [0x00, 0x00])
        packet = [self.BROADCAST] + pl + [self.INSTR_FAST_BULK_READ] + p
        return self.send(packet)
