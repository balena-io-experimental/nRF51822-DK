#!/bin/bash

#Erase memory
nrfjprog -e

#Flash softdevice
cd /opt/nRF5_SDK_11.0.0_89a8197/components/softdevice/s130/hex
nrfjprog --program s130_nrf51_2.0.0_softdevice.hex -f nrf51 --chiperase

#Flash DFU bootloader
cd /opt/nRF5_SDK_11.0.0_89a8197/examples/dfu/bootloader/pca10028/dual_bank_ble_s130/armgcc
make
nrfjprog --family nRF51 --program _build/nrf51422_xxac.hex
nrfjprog --family nRF51 -r
