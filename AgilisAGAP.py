#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
from tango import AttrWriteType, DevState, DispLevel, DevFloat, Except, DevError
from tango.server import Device, attribute, command, device_property
from time import sleep
import serial


class  AgilisAGAP(Device):

    Address = device_property(
        dtype='int16',
    )
    Port = device_property(
        dtype='str',
    )

# some Constants
    __AXIS_X = 'U'
    __AXIS_Y = 'V'

# Errors from page 64 of the manual
    __ERROR_NEG_END_OF_RUN = 1
    __ERROR_POS_END_OF_RUN = 2
    __ERROR_OUT_OF_RANGE   = ('G', 'C')

# States from page 65 of the manual
    __STATE_READY   = ('32', '33', '34', '35', '36')
    __STATE_MOVING  = ('28', '29')
    
    position_x = attribute(
        label='Position X',
        dtype='float',
        access=AttrWriteType.READ_WRITE,
        format="%4.3f",
        doc = 'absolute position X'
    )
    position_y = attribute(
        label='Position Y',
        dtype='float',
        access=AttrWriteType.READ_WRITE,
        format="%4.3f",
        doc = 'absolute position Y'
    )

    def init_device(self):
        Device.init_device(self)

        self.set_state(DevState.INIT)
        try:
            self.info_stream("Connecting to AgilisAGAP on port: {:s} ...".format(self.Port))
            self.serial = serial.Serial(
                port = self.Port,
                baudrate = 921600,
                bytesize = 8,
                stopbits = 1,
                parity = 'N',
                xonxoff = True,
                timeout = 0.05)
            if self.serial.isOpen():
                self.serial.close()
            self.serial.open()
            self.info_stream("Success!")
            self.info_stream('Connection established:\n{:s}\n{:s}'.format(self.query('ID?'), self.query('VE?')))
        except:
            self.error_stream("Cannot connect!")
            self.set_state(DevState.OFF)
       
        self.set_state(DevState.ON)        

    def delete_device(self):
        if self.serial.isOpen():
            self.serial.close()
            self.info_stream('Connection closed for port {:s}'.format(self.Port))

    def always_executed_hook(self):
        res = self.query('TS?')
        if (res != ''):
            err = int(res[:4],16)
            state = res[4:]
            if (state in self.__STATE_MOVING):
                self.set_status('Device is MOVING')
                self.set_state(DevState.MOVING)
            elif (state in self.__STATE_READY):
                self.set_status('Device is ON')
                self.set_state(DevState.ON)
            else:
                self.set_status('Device is UNKOWN')
                self.set_state(DevState.UNKNOWN)

    def read_position_x(self):
        return float(self.query('TP' + self.__AXIS_X + '?'))

    def write_position_x(self, value):
        self.query('PA' + self.__AXIS_X + str(value))
        err = self.get_cmd_error_string()
        if err in self.__ERROR_OUT_OF_RANGE:
            self.set_state(DevState.ON)
            self.set_status('x position out of range')
        else:
            self.set_state(DevState.MOVING)  

    def read_position_y(self):
        return float(self.query('TP' + self.__AXIS_Y + '?'))

    def write_position_y(self, value):
        self.query('PA' + self.__AXIS_Y + str(value))
        err = self.get_cmd_error_string()
        if err in self.__ERROR_OUT_OF_RANGE:
            self.set_state(DevState.ON)
            Except.throw_exception('y position out of range')
        else:
            self.set_state(DevState.MOVING)
        
    @command
    def stop_motion(self):
        self.send_cmd('ST')
        
    @command()    
    def reset(self):
        self.send_cmd('RS')

    def query(self, cmd):
        prefix = str(self.Address) + cmd[:-1]
        self.send_cmd(cmd)
        answer = self.serial.readline().decode('utf-8')
        if answer.startswith(prefix):
           answer = answer[len(prefix):].strip()
        else:
           answer = ''
        return answer
    
    def send_cmd(self, cmd):
        cmd = str(self.Address) + cmd + '\r\n'
        self.serial.flushInput()
        self.serial.flushOutput()
        self.serial.write(cmd.encode('utf-8'))
        self.serial.flush()                  

    def get_cmd_error_string(self):
        error = self.query('TE?')
        return error.strip()


# start the server
if __name__ == '__main__':
    AgilisAGAP.run_server()
