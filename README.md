# System Info Display

Display basic system information and energy meter readings (fetched via [IOBroker][]) on a ST7735 OLED display (using [luma.oled][]).
This is a re-implementation of "System Info Display" by [Alvaro Valdebenito][avaldebe].

[IOBroker]: https://www.iobroker.net/#en/download
[luma.oled]: https://github.com/rm-hull/luma.oled

## ST7735 on a Raspberry Pi

After `sys_info.py` is called, the display will be updated once a minute.

### Hardware Setup ###
This script is built for a ST7735 OLED display. Please make sure your wiring is correct. The wiring below is for a 1.77" OLED offered by AZ Delivery.

![ST7735 wiring](assets/rpi-wiring.png?raw=true "ST7735 wiring for AZ-Delivery 1.77" LCD")

| TFT LCD pin | RaspberryPi pin | wire color |
| --- | --- | --- |
| LEDA | 3.3v (pin 1) | orange |
| CS (SS) | GOIO 8 / CE0 (pin 24) | cyan |
| RS (Reg. Sel.) | GPIO 23 (pin 16) | purple |
| RES (Reset) | GPIO 24 (pin 18) | blue |
| SDA (MOSI) | GPIO 10 / MOSI (pin 19) | green |
| SCK | GPIO 11 / SCLK (pin 23) | pink |
| VCC | 5v (pin 4) | red |
| GND | GND (pin 25) | black |

### Installation for python3

[luma.oled][install.oled]

```bash
sudo apt install python3-dev python3-pip libfreetype6-dev libjpeg-dev build-essential
sudo -H pip3 install --upgrade luma.oled
```

Additional dependencies on [Raspbian Stretch Lite][raspbian]

```bash
sudo apt install libopenjp2-7 libtiff5
sudo -H pip3 install psutil
```

[install.oled]: https://luma-oled.readthedocs.io/en/latest/install.html
[raspbian]: https://www.raspberrypi.org/downloads/raspbian/

### Customize Script ###
Energy Meter readings are fetched via IOBroker. Please make sure to setup an energy meter adapter in IOBroker and change the energy meter objects in `sys_info.py` line 54 and line 56 to the object names in your IOBroker instance.

### Start after boot

There are different options to start a job after boot, see [here](howto).
This are the ones I have tried/plan to try out.

- cronjob: easy to set-up, need to reboot to update the script
- service: harder to set-up, easy to start/stop

[howto]: https://www.dexterindustries.com/howto/run-a-program-on-your-raspberry-pi-at-startup/

#### Run as a cronjob

Add the following lines to your crontab (`crontab -e`)

```crontab
@reboot bash -lc $HOME/RpiHwMeterMonitor/sys_info.py &
```

The `bash -l` is needed to get the right `$PATH` for `iwconfig`,
which in turn is needed for the wifi signal strength.

#### Run as a service

 The `systemd` service file ([RpiHwMeterMonitor.service](RpiHwMeterMonitor.service))
 defines a new service called RpiHwMeterMonitor,
 which is to be launched once the multi-user environment is available.

```bash
# copy the service file
sudo cp RpiHwMeterMonitor.service /lib/systemd/system/

# set the required permissions
sudo chmod 644 /lib/systemd/system/RpiHwMeterMonitor.service

# enhable new service
sudo systemctl daemon-reload

# start/stop/reload service
sudo systemctl start RpiHwMeterMonitor
sudo systemctl stop RpiHwMeterMonitor
sudo systemctl reload-or-restart RpiHwMeterMonitor

# check service status
systemctl status RpiHwMeterMonitor

# start automatically after reboot
sudo systemctl enable RpiHwMeterMonitor # start after reboot
#sudo systemctl disable RpiHwMeterMonitor # don't start
sudo reboot
```

For more info about `systemctl` usage, see this [tutorial][systemctl],
and this article about [auto restart crashed services][restart].

[systemctl]: https://www.digitalocean.com/community/tutorials/how-to-use-systemctl-to-manage-systemd-services-and-units
[restart]: https://singlebrook.com/2017/10/23/auto-restart-crashed-service-systemd/
