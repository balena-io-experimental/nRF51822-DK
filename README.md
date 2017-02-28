# nRF51822-DK
edge-node-manager compatible firmware for the nRF51822-DK

### Getting started
 - Ensure you have [Docker](https://www.docker.com/) installed on your local machine and the daemon is running
 - Ensure you have the [nRF5x command line tools](https://infocenter.nordicsemi.com/topic/com.nordic.infocenter.tools/dita/tools/nrf5x_command_line_tools/nrf5x_installation.html) installed and in your path
 - Sign up on [resin.io](https://dashboard.resin.io/signup)
 - Work through the [getting started guide](https://docs.resin.io/raspberrypi3/nodejs/getting-started/)
 - Create a dependent application called `nrf51822dk`
 - Set these variables in the `Fleet Configuration` dependent application side tab
    - `RESIN_SUPERVISOR_DELTA=1`
    - `RESIN_HOST_TYPE=nrf51822dk`
 - Clone this repository to your local workspace
 - Add the dependent application `resin remote` to your local workspace
 - Retrieve the dependent application ID from the Resin dashboard, for example: If your dependent application URL is
 `https://dashboard.staging.io/apps/13829/devices` the ID is `14495`
 - Change [line 33](https://github.com/resin-io-projects/nRF51822-DK/blob/master/source/main.c#L33) in `source/main.c` `#define APP_ID "1234567890"` to point to your dependent application ID e.g. `#define APP_ID "14495"`
 - Connect the nRF51822-DK to your computer using a USB cable
 - Run the provisioning script `$ ./provision.sh`, this will generate the initial firmware and flash the nRF51822-DK
 - Push code to resin as normal :)
