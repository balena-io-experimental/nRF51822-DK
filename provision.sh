#!/bin/bash

# Compile application
docker build -t provision -f Dockerfile.provision ./
docker run -v $(pwd):/out provision

# Erase the device
nrfjprog --eraseall

# Flash soft device and bootloader
nrfjprog --program merged.hex --chiperase --verify --reset

# Flash application
nrfjprog --program application.hex --verify

# Let the bootloader know the application is valid
nrfjprog --memwr 0x3fc00 --val 0x01

# Clean up
rm -rf application.hex
