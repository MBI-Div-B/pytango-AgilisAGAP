# pytango-AgilisAGAP

This is a tango device server for a Newport Conex Agilis AGAP piezo mirror with controller.


When defining a new udev rule for tty, you need to add the product id and vendor id to linux known list of devices.

For this you need to edit the file /sys/bus/usb-serial/drivers/ftdi_sio/new_id

you need to add:

[vendor id] [product id]




https://arduino.stackexchange.com/questions/91181/hm-10-serial-question

