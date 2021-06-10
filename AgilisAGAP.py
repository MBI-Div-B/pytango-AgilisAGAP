#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) DATE  MBI-Division-B
# MIT License, refer to LICENSE file
# Author: / Email: (please set DATE above to year)

__all__ = ["AgilisAGAP", "main"]

# PyTango imports
import PyTango
from PyTango import DebugIt, DeviceProxy
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command, pipe
from PyTango.server import class_property, device_property
from PyTango import AttrQuality,DispLevel, DevState
from PyTango import AttrWriteType, PipeWriteType
# Additional import
# PROTECTED REGION ID(AgilisAGAP.additionnal_import) ENABLED START #
from time import sleep
import serial
# PROTECTED REGION END #    //  AgilisAGAP.additionnal_import

flagDebugIO = 0


class  AgilisAGAP(Device):
    """ 
    Tangodevice AgilisAGAP

    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(AgilisAGAP.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  AgilisAGAP.class_variable
    # ----------------
    # Class Properties

    # ----------------

    # read name of serial port ('com1' .. (Windows) or '/dev/ttyUSB0' .. (Linux)) 
    # read the address of the device (1..31)

# -----------------
    # Device Properties
    # -----------------

    Address = device_property(
        dtype='int16',
    )
    Port = device_property(
        dtype='str',
    )


# some Constants
    __EOL = '\r\n'
    __AXIS_X = 'U'
    __AXIS_Y = 'V'


# time to wait after sending a command.
    COMMAND_WAIT_TIME_SEC = 0.05  # 0.06

# Errors from page 64 of the manual
    __ERROR_NEG_END_OF_RUN = 1
    __ERROR_POS_END_OF_RUN = 2
    __ERROR_OUT_OF_RANGE   = ('G', 'C')

# States from page 65 of the manual
    __STATE_NOT_REFERENCED = ('3C', '0A', '0B', '0c' ,'0D', '0E', '0F', '10')
    __STATE_READY   = ('32', '33', '34', '35', '36')
    __STATE_MOVING  = ('28', '29')
    
# some private variables
    __ser_port = None
    __AGAPID    = ''
    __port     = ''
    
    __AGAP_state    = ''
    __error        = ''
    
# private status variables, updated by "get_smc__state()"
    __Motor_Run   = False
    __Ready       = False
    __Out_Of_Limit= False
    __Pos_X       = 0.000
    __Pos_Y       = 0.000
    
    
    
    # ----------
    # Attributes
    # ----------

    out_of_limits = attribute(
        dtype='bool',
        doc = 'if the new set position out of range\n when this flag is true'
    )
    
    moving = attribute(
        dtype='bool',
        doc = 'if motor in moving this flag is true'
    )
    position_x = attribute(
        dtype='float',
        access=AttrWriteType.READ_WRITE,
        format="%4.3f",
        doc = 'absolute position'
    )
    position_y = attribute(
        dtype='float',
        access=AttrWriteType.READ_WRITE,
        format="%4.3f",
        doc = 'absolute position'
    )
    
    ready = attribute(
        dtype='bool',
        doc = 'READY state'
    )
    
    
    # -----
    # Pipes
    # -----

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        Device.init_device(self)
        # PROTECTED REGION ID(AgilisAGAP.init_device) ENABLED START #
        
        self.proxy = DeviceProxy(self.get_name())
        
        self.__AGAPID = str(self.Address)
        self.__port  = self.Port
        
        if flagDebugIO:
            print("Get_name: %s" % (self.get_name()))
            print("Connecting to AgilisAGAP on %s" %(self.__port))
            print("Device address: %s" %(self.__AGAPID))
            
        self.__ser_port = serial.Serial(
            port = self.__port,
            baudrate = 921600,
            bytesize = 8,
            stopbits = 1,
            parity = 'N',
            xonxoff = True,
            timeout = 0.050)    
        
        
        if self.__ser_port.isOpen():
            self.__ser_port.close()
        self.__ser_port.open()
        
        if ("CONEX-AGAP" in self.read_controller_info()):
            self.get_AGAP_state()
            self.read_position_x()
            self.read_position_y()
            self.set_state(PyTango.DevState.ON)  
        else:
            self.set_state(PyTango.DevState.OFF)
        
        
        if flagDebugIO:
            print ("Run: ",self.__Motor_Run)
            print ("Postion_X: ", self.__Pos_X)
            print ("Postion_Y: ", self.__Pos_Y)  
            
        # PROTECTED REGION END #    //  AgilisAGAP.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(AgilisAGAP.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  AgilisAGAP.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(AgilisAGAP.delete_device) ENABLED START #
        if self.__ser_port.isOpen():
            self.__ser_port.close()
        # PROTECTED REGION END #    //  AgilisAGAP.delete_device
    
    
   
    def send_cmd(self, cmd):
        # PROTECTED REGION ID(AgilisAGAP.send_cmd) ENABLED START #
        snd_str = cmd + self.__EOL
        self.__ser_port.flushOutput()
        self.__ser_port.write(snd_str.encode('utf-8'))
        self.__ser_port.flush()
        # PROTECTED REGION END #    //  AgilisAGAP.send_cmd    

    def get_position(self,Axis):
        pos = self.write_read('TP' + Axis + '?')
        if pos != '':
            if Axis == self.__AXIS_X:
                self.__Pos_X = float(pos)   
            else:
                self.__Pos_Y = float(pos)                       

    def get_cmd_error_string(self):
        error = self.write_read('TE?')
        return error.strip()
        
        
    # ------------------
    # Attributes methods
    # ------------------
    def read_out_of_limits(self):
        # PROTECTED REGION ID(AgilisAGAP.read_out_of_limits) ENABLED START #
        return self.__Out_Of_Limits
        # PROTECTED REGION END #    //  AgilisAGAP.read_out_of_limits
    
    def read_moving(self):
        # PROTECTED REGION ID(AgilisAGAP.moving_read) ENABLED START #
        return self.__Motor_Run
        # PROTECTED REGION END #    //  AgilisAGAP.moving_read

    def read_position_x(self):
        # PROTECTED REGION ID(AgilisAGAP.position_read) ENABLED START #
        return self.__Pos_X
        # PROTECTED REGION END #    //  AgilisAGAP.position_read

    def read_position_y(self):
        # PROTECTED REGION ID(AgilisAGAP.position_read) ENABLED START #
        return self.__Pos_Y
        # PROTECTED REGION END #    //  AgilisAGAP.position_read

    def write_position_x(self, value):
        # PROTECTED REGION ID(AgilisAGAP.position_write) ENABLED START #
        self.write_read('PA' + self.__AXIS_X + str(value))
        tmp = self.get_cmd_error_string()
        if tmp in self.__ERROR_OUT_OF_RANGE:
            self.__Out_Of_Limits = True
        else:
            self.__Out_Of_Limits = False
            self.__Motor_Run = True
            
        # PROTECTED REGION END #    //  AgilisAGAP.position_write
    
    def write_position_y(self, value):
        # PROTECTED REGION ID(AgilisAGAP.position_write) ENABLED START #
        self.write_read('PA' + self.__AXIS_Y + str(value))
        tmp = self.get_cmd_error_string()
        if tmp in self.__ERROR_OUT_OF_RANGE:
            self.__Out_Of_Limits = True
        else:
            self.__Out_Of_Limits = False     
        # PROTECTED REGION END #    //  AgilisAGAP.position_write
        
    def read_ready(self):
        # PROTECTED REGION ID(AgilisAGAP.homing_read) ENABLED START #
        return self.__Ready
        # PROTECTED REGION END #    //  AgilisAGAP.homing_read
    # -------------
    # Pipes methods
    # -------------

    # --------
    # Commands
    # --------
    @command(dtype_in=str, 
    dtype_out=str, 
    )
    @DebugIt()
    def write_read(self, argin):
        # PROTECTED REGION ID(AgilisAGAP.write_read) ENABLED START #
        # if argin ended with "?", then we expected an answer
        response = (argin[-1] == '?')
        if response:
            # cut the "?"
            prefix = self.__AGAPID + argin[:-1]
            send_str = self.__AGAPID + argin
            self.__ser_port.flushInput()
            self.send_cmd(send_str)
            tmp_answer = self.__ser_port.readline().decode('utf-8')
            if tmp_answer.startswith(prefix):
                answer = tmp_answer[len(prefix):]
            else:
                answer = ''    
        else:    
            send_str = self.__AGAPID + argin
            self.send_cmd(send_str)
            answer = ''
        return answer
        # PROTECTED REGION END #    //  AgilisAGAP.write_read
        
    # this command stops both X and Y axes at the same time
    @command
    @DebugIt()
    def stop_motion(self):
        # PROTECTED REGION ID(AgilisAGAP.stop_motion) ENABLED START #
        self.write_read('ST')
        # PROTECTED REGION END #    //  AgilisAGAP.stop_motion
    
    
    @command (
    dtype_out=str, polling_period= 200, doc_out='state of AgilisAGAP' ) 
    @DebugIt()
    def get_AGAP_state(self):
        # PROTECTED REGION ID(AgilisAGAP.get_AGAP_state) ENABLED START #
        self.get_position(self.__AXIS_X)
        # sleep eingebaut 
        sleep(COMMAND_WAIT_TIME_SEC)
        self.get_position(self.__AXIS_Y)
        # sleep eingebaut 
        sleep(COMMAND_WAIT_TIME_SEC)
        resp = ''
        resp = self.write_read('TS?')
        if (resp != ''):
            self.__error = int(resp[:4],16)
            self.__AGAP_state = resp[4:].strip()
            if (self.__AGAP_state in self.__STATE_MOVING):
                self.__Motor_Run   = True
            else:
                self.__Motor_Run   = False
            if self.__AGAP_state in self.__STATE_READY:
                self.__Ready  = True
            else:
                self.__Ready  = False           
        return resp
        # PROTECTED REGION END #    //  AgilisAGAP.get_AGAP_state

    # @command
    # @DebugIt()
    # def homing(self):
    #     # PROTECTED REGION ID(AgilisAGAP.homing) ENABLED START #
    #     self.write_read('OR')
    #     # PROTECTED REGION END #    //  AgilisAGAP.homing
    
    @command(dtype_out=str)
    @DebugIt()
    def reset(self):
        # PROTECTED REGION ID(AgilisAGAP.reset) ENABLED START #
        self.write_read('RS')
        return ("Device reset!")
        # PROTECTED REGION END #    //  AgilisAGAP.reset
    
    @command(dtype_out=str)
    @DebugIt()
    def read_controller_info(self):
        return (self.write_read('VE?'))
    
    @command(dtype_out=str)
    @DebugIt()    
    def read_controller_identifier(self):
        return (self.write_read('ID?'))
# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(AgilisAGAP.main) ENABLED START #
    from PyTango.server import run
    return run((AgilisAGAP,), args=args, **kwargs)
    # PROTECTED REGION END #    //  AgilisAGAP.main

if __name__ == '__main__':
    main()
