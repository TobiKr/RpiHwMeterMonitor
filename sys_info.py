#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Display basic system and energy meter information.
- host: nodename kernel-release (same as `uname -nr`)
- ip: IP address
- cpu: mean CPU load [%], calulcated as 1 min mean load / number of cores * 100
- mem: memory usage [%], calculated as (total - available) / total * 100
- disk: disk usage [%]
- temp: CPU temperature [°C]
- meter1/2: Energy Meter from IOBroker in Kilowatt/hour
- datetimenow: current date and time 
"""

import os
import time
import psutil
import socket
import subprocess
import json
from datetime import datetime
from PIL import ImageFont
try:
    from luma.core.interface.serial import spi
    from luma.lcd.device import st7735
finally:
    from luma.core.render import canvas

def sinfo(key):
    """
    Basic system information
    """

    host = lambda : '{0[1]} {0[2]}'.format(os.uname())

    ip = lambda : 'IP: ' + socket.gethostbyname('%s.local'%socket.gethostname())

    wifi = lambda : subprocess.check_output(
        "/sbin/iwconfig wlan0 2>/dev/null | grep Signal | sed 's:.*=::'",
        shell=True,
    ).decode('UTF-8').replace('dBm', '').strip() or 'N/A'

    cpu = lambda : '%.0f%%'%(os.getloadavg()[0]/os.cpu_count()*100)

    mem = lambda : 'MEM: %.0f%%' %psutil.virtual_memory().percent

    disk = lambda : '%.0f%%'%psutil.disk_usage("/").percent

    temp = lambda : subprocess.check_output(
        """/usr/bin/awk '{printf "%.0f°C", $0/1000}' < /sys/class/thermal/thermal_zone0/temp""",
        shell=True,
    ).decode('UTF-8')

    meter1 = lambda: 'Z1 ' + str(getIoBrokerObjectState('0_userdata.0.Zaehler1_Test'))

    meter2 = lambda: 'Z2 ' + str(getIoBrokerObjectState('0_userdata.0.Zaehler2_Test'))

    datetimenow = lambda: datetime.now().strftime("%d.%m.%y %H:%M:%S")

    try:
        return dict(host=host, ip=ip, wifi=wifi, cpu=cpu, mem=mem, disk=disk, temp=temp, meter1=meter1, meter2=meter2, datetimenow=datetimenow)[key]
    except KeyError:
        return None

def getIoBrokerObjectState(object):
    state = subprocess.check_output(
        "/usr/bin/iobroker state get " + object,
        shell=True,
    ).decode('UTF-8')
    state_dict = json.loads(state)
    return state_dict['val']

def stats(device, info, font):
    """
    draw system info to canvas
    """
    with canvas(device) as draw:
        for (x, y, icon, dx, dy, size, fn) in info:
            if icon:
                draw.text((x, y), icon, font=font['icon_%s'%size], fill="white", spacing=3)
            if fn:
                x += dx; y += dy
                draw.text((x, y), fn(), font=font['text_%s'%size], fill="white", spacing=3)


def main():
    s = spi(port=0, device=0, gpio_DC=23, gpio_RST=24)
    device=st7735(s,rotate=2,width=160,height=128,h_offset=0,v_offset=0,bgr=False)
    device.backlight(False)
    forever = True

    # custom fonts
    font_path = "%s/fonts/%%s"%os.path.dirname(__file__)
    font = dict(
        text_small = ImageFont.truetype(font_path%'Montserrat-Light.ttf', 12),
        text_large = ImageFont.truetype(font_path%'Montserrat-Medium.ttf', 19),
        icon_small = ImageFont.truetype(font_path%'fontawesome-webfont.ttf', 14),
        icon_large = ImageFont.truetype(font_path%'fontawesome-webfont.ttf', 19),
    )

    # layout: (x, y, icon, dx, dy, size, function)
    info = (
        ( 0, 2, None     ,  0,  0, 'small', sinfo('ip')),
        ( 0, 23, '\uf2db', 22,  0, 'small', sinfo('cpu')),
        ( 0, 41, None    ,  0,  0, 'small', sinfo('mem')),
        ( 2, 64, '\uf0e7', 12,  0, 'small', sinfo('meter1')),
        #(95, 2, '\uf1eb' , 22,  0, 'small', sinfo('wifi')),
        (87, 41, '\uf1c0', 22,  0, 'small', sinfo('disk')),
        (89, 23, '\uf2c8', 22,  0, 'small', sinfo('temp')),
        (89, 64, '\uf0e7', 12,  0, 'small', sinfo('meter2')),
        ( 0,108, '\uf017', 18,  0, 'small', sinfo('datetimenow')),
    )

    stats(device, info, font)
    time.sleep(5)  # 1st update after 5s
    while forever:
        stats(device, info, font)
        time.sleep(60) # update every 60 sec


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass