import struct
import threading
import time

import serial

from pydobot.message import Message

MODE_PTP_JUMP_XYZ = 0x00
MODE_PTP_MOVJ_XYZ = 0x01
MODE_PTP_MOVL_XYZ = 0x02
MODE_PTP_JUMP_ANGLE = 0x03
MODE_PTP_MOVJ_ANGLE = 0x04
MODE_PTP_MOVL_ANGLE = 0x05
MODE_PTP_MOVJ_INC = 0x06
MODE_PTP_MOVL_INC = 0x07
MODE_PTP_MOVJ_XYZ_INC = 0x08
MODE_PTP_JUMP_MOVL_XYZ = 0x09


class Dobot(threading.Thread):
    on = True
    x = 0.0
    y = 0.0
    z = 0.0
    r = 0.0
    j1 = 0.0
    j2 = 0.0
    j3 = 0.0
    j4 = 0.0

    # joint_angles = [4]

    def __init__(self, port, verbose=False):
        threading.Thread.__init__(self)
        self.verbose = verbose
        self.lock = threading.Lock()
        self.ser = serial.Serial(port,
                                 baudrate=115200,
                                 parity=serial.PARITY_NONE,
                                 stopbits=serial.STOPBITS_ONE,
                                 bytesize=serial.EIGHTBITS)
        is_open = self.ser.isOpen()
        if self.verbose:
            print('pydobot: %s open' % self.ser.name if is_open else 'failed to open serial port')
        self._set_ptp_coordinate_params(velocity=200.0, acceleration=200.0)
        self._set_ptp_common_params(velocity=200.0, acceleration=200.0)
        self.start()

    def run(self):
        while self.on:
            self._get_pose()
            time.sleep(0.2)

    def close(self):
        self.on = False
        self.lock.acquire()
        self.ser.close()
        if self.verbose:
            print('pydobot: %s closed' % self.ser.name)
        self.lock.release()

    def _send_command(self, msg):
        self.lock.acquire()
        self._send_message(msg)
        response = self._read_message()
        self.lock.release()
        return response

    def _send_message(self, msg):
        time.sleep(0.1)
        if self.verbose:
            print('pydobot: >>', msg)
        self.ser.write(msg.bytes())

    def _read_message(self):
        time.sleep(0.1)
        b = self.ser.read_all()
        if len(b) > 0:
            msg = Message(b)
            if self.verbose:
                print('pydobot: <<', msg)
            return msg
        return

    def _get_pose(self):
        msg = Message()
        msg.id = 10
        response = self._send_command(msg)
        self.x = struct.unpack_from('f', response.params, 0)[0]
        self.y = struct.unpack_from('f', response.params, 4)[0]
        self.z = struct.unpack_from('f', response.params, 8)[0]
        self.r = struct.unpack_from('f', response.params, 12)[0]
        self.j1 = struct.unpack_from('f', response.params, 16)[0]
        self.j2 = struct.unpack_from('f', response.params, 20)[0]
        self.j3 = struct.unpack_from('f', response.params, 24)[0]
        self.j4 = struct.unpack_from('f', response.params, 28)[0]
        if self.verbose:
            print("pydobot: x:%03.1f y:%03.1f z:%03.1f r:%03.1f j1:%03.1f j2:%03.1f j3:%03.1f j4:%03.1f" %
                  (self.x, self.y, self.z, self.r, self.j1, self.j2, self.j3, self.j4))
        return response

    def _set_cp_cmd(self, x, y, z):
        msg = Message()
        msg.id = 91
        msg.ctrl = 0x03
        msg.params = bytearray(bytes([0x01]))
        msg.params.extend(bytearray(struct.pack('f', x)))
        msg.params.extend(bytearray(struct.pack('f', y)))
        msg.params.extend(bytearray(struct.pack('f', z)))
        msg.params.append(0x00)
        return self._send_command(msg)

    def _set_ptp_coordinate_params(self, velocity, acceleration):
        msg = Message()
        msg.id = 81
        msg.ctrl = 0x03
        msg.params = bytearray([])
        msg.params.extend(bytearray(struct.pack('f', velocity)))
        msg.params.extend(bytearray(struct.pack('f', velocity)))
        msg.params.extend(bytearray(struct.pack('f', acceleration)))
        msg.params.extend(bytearray(struct.pack('f', acceleration)))
        return self._send_command(msg)

    def _set_ptp_common_params(self, velocity, acceleration):
        msg = Message()
        msg.id = 83
        msg.ctrl = 0x03
        msg.params = bytearray([])
        msg.params.extend(bytearray(struct.pack('f', velocity)))
        msg.params.extend(bytearray(struct.pack('f', acceleration)))
        return self._send_command(msg)

    def _set_ptp_cmd(self, x, y, z, r, mode):
        msg = Message()
        msg.id = 84
        msg.ctrl = 0x03
        msg.params = bytearray([])
        msg.params.extend(bytearray([mode]))
        msg.params.extend(bytearray(struct.pack('f', x)))
        msg.params.extend(bytearray(struct.pack('f', y)))
        msg.params.extend(bytearray(struct.pack('f', z)))
        msg.params.extend(bytearray(struct.pack('f', r)))
        return self._send_command(msg)

    def _set_end_effector_suction_cup(self, suck=False):
        msg = Message()
        msg.id = 62
        msg.ctrl = 0x03
        msg.params = bytearray([])
        msg.params.extend(bytearray([0x01]))
        if suck is True:
            msg.params.extend(bytearray([0x01]))
        else:
            msg.params.extend(bytearray([0x00]))
        return self._send_command(msg)

    def set_infrared_sensor(self):
        msg = Message()
        msg.id = 138
        msg.ctrl = 0x02
        msg.params = bytearray([])
        msg.params.extend(bytearray([0x00])) # enable
        msg.params.extend(bytearray([0x01])) # port2
        return self._send_command(msg)

    def get_infrared_sensor(self):
        msg = Message()
        msg.id = 138
        msg.ctrl = 0x00
        msg.params = bytearray([])
        msg.params.extend(bytearray([0x01])) # port2
        msg.params.extend(bytearray([0x01])) # value
        response = self._send_command(msg)
        # return response
        print(response)
        return struct.unpack_from('?', response.params, 0)[0]

    # def get_io(self):
    #     msg = Message()
    #     msg.id = 130
    #     msg.ctrl = 0x00
    #     response = self._send_command(msg)
    #     print(response)       

    def set_color_sensor(self):
        msg = Message()
        msg.id = 137
        msg.ctrl = 0x02
        msg.params = bytearray([])
        msg.params.extend(bytearray([0x00])) # enable
        msg.params.extend(bytearray([0x03])) # port5
        return self._send_command(msg)

    def get_color_sensor(self):
        msg = Message()
        msg.id = 137
        msg.ctrl = 0x00
        response = self._send_command(msg)
        # return response
        print(response)
        return struct.unpack_from('?', response.params, 0)[0]

    def stop_conveyor_belt(self):
        self._set_stepper_motor(0)

    def move_conveyor_belt(self, speed, direction=1):
        if 0.0 <= speed <= 1.0 and (direction == 1 or direction == -1):
            STEP_PER_CRICLE = 360.0 / 1.8 * 10.0 * 16.0
            MM_PER_CRICLE = 3.1415926535898 * 36.0
            motor_speed = 70 * speed * STEP_PER_CRICLE / MM_PER_CRICLE * direction
            self._set_stepper_motor(motor_speed)
        else:
            print("Wrong Parameter")

    def _set_stepper_motor(self, speed):
        msg = Message()
        msg.id = 135
        msg.ctrl = 0x03 
        msg.params = bytearray([])
        msg.params.extend(bytearray([0x00]))
        msg.params.extend(bytearray([0x01]))
        print(speed)
        msg.params.extend(bytearray(struct.pack('i', int(speed))))
        return self._send_command(msg)

    def go(self, x, y, z, r=0.):
        self._set_ptp_cmd(x, y, z, r, mode=MODE_PTP_MOVJ_XYZ)

    def suck(self, suck):
        self._set_end_effector_suction_cup(suck)

    def speed(self, velocity=100., acceleration=100.):
        self._set_ptp_common_params(velocity, acceleration)
        self._set_ptp_coordinate_params(velocity, acceleration)
