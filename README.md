# nRF51822
edge-node-manager compatible firmware for the nRF51822

### Modify firmware to point to your application
 - Change line 46 `#define DEVICE_NAME "13693"` in `src/main.c` to point to your applicationUUID

### Prepare a fresh nRf51822
 - Ensure you have the dependancies listed in the `Dockerfile`
 - Plug the board into your computer using the USB cable
 - Prepare the board `$ sudo ./scripts/prepare.sh`

### Compile firmware on your machine
 - Ensure you have the dependancies listed in the `Dockerfile`
 - Compile the firmware `$ make`

### Flash firmware on your machine over-the-air
 - Ensure you have the dependancies listed in the `Dockerfile`
 - Compile the firmware
 - Power the board using the USB cable but DO NOT connect it to your computer
 - Enable bluetooth `$ hciconfig hci0 up`
 - Get the board address `$ hcitool lescan`
 - Find the board address where the name is `DfuTarg` e.g. `EE:50:F0:F8:3C:00 DfuTarg`
 - `$ python2 scripts/update.py -a EE:50:F0:F8:3C:00 -z application.zip` (It won't work with python3, you must use python2)
