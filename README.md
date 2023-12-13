# pytango-AgilisAGAP

This is a tango device server for a Newport Conex Agilis AGAP piezo mirror with controller.


When defining a new udev rule for tty, you need to add the product id and vendor id to linux known list of devices.

For this you need to add the following TWO udev rules (adjust idProduct, idVendor and serial). YOU NEED BOTH!!!

ACTION=="add|change", ATTRS{idVendor}=="104d", ATTRS{idProduct}=="3008", ATTRS{serial}=="A61YC2A5", RUN+="/sbin/modprobe ftdi_sio", RUN+="/bin/sh -c 'echo 104d 3008 > /sys/bus/usb-serial/drivers/ftdi_sio/new_id'"

ACTION=="add|change", SUBSYSTEM=="tty", ATTRS{idVendor}=="104d", ATTRS{idProduct}=="3008", ATTRS{serial}=="A61YC2A5", SYMLINK+="ttyAGILISAGAP1", MODE="0666"
