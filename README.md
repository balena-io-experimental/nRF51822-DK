# nRF51822-DK
edge-node-manager compatible firmware for the nRF51822-DK

### Modify firmware
 - Change [line 46](https://github.com/resin-io-projects/nRF51822-DK/blob/master/src/main.c#L46) in `src/main.c` to point to your dependant application UUID

### Prepare nRF51822-DK
 - Ensure you have the dependancies listed in the `Dockerfile`
 - Connect the nRF51922-DK to your computer using the USB cable
 - Prepare the board `$ sudo ./scripts/prepare.sh`

### Compile firmware
 - Ensure you have the dependancies listed in the `Dockerfile`
 - Compile the firmware `$ make`

### Flash firmware
 - Compile the firmware
 - Connect the nRF51822-DK to your computer using the USB cable
 - Enable bluetooth `$ hciconfig hci0 up`
 - Get the board address `$ hcitool lescan`
 - Find the board address where the name is `DfuTarg` e.g. `EE:50:F0:F8:3C:00 DfuTarg`
 - Flash firmware `$ python2 scripts/update.py -a EE:50:F0:F8:3C:00 -z application.zip`
 - Warn: You must use python2.7
 - Note: If the process times out or hangs please try to run the script again, the OTA update will continue from where it left off

### Getting started
 - Note: Take a look at the [edge-node-manager](https://github.com/resin-io/edge-node-manager) if you havn't already done so
 - Create a new dependant application called `nRF51822DK` from the `Dependant Applications` tab accessed from the side bar
 - Add the dependent application `resin remote` to your local workspace using the useful shortcut in the dashboard UI, for example:
```
$ git remote add resin gh_josephroberts@git.resinstaging.io:gh_josephroberts/nrf51822DK.git
```
 - Retrive the dependent application `UUID` from the Resin dashboard, for example: If your dependant application URL is
 `https://dashboard.resinstaging.io/apps/13829/devices` the `UUID` is `14495`
 - Set the dependent application `UUID` on [line 82](https://github.com/resin-io/edge-node-manager/blob/master/application/application.go#L82)
  in `application/application.go` to point to your dependant application, for example: `initApplication(14495, board.NRF51822DK)`
 - Make sure you add, commit and push the change to the edge-node-manager application
 - Add, commit and push the `nRF51822DK` application to your RPi3, for example:
```
$ git add src/main.c
$ git commit -m "Set the application UUID"
$ git push resin master
```
 - Turn on your nRF51822-DK dependent device within range of the RPi3 gateway device and watch it appear on the Resin dashboard!
