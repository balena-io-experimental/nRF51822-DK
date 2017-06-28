# nrf51822dk base image
# See more about resin base images here: http://docs.resin.io/runtime/resin-base-images/
FROM resin/nrf51822dk AS buildstep

# Set the working directory
WORKDIR /usr/src/app

# Copy make file to the working directory
COPY Makefile ./

# Copy config files to the working directory
COPY config/ ./config

# Copy source files to the working directory
COPY source/ ./source

# Compile the firmware
RUN make && \
	nrfutil dfu genpkg --application _build/nrf51422_xxac_s130.hex /assets/application.zip

# Start with a minimal runtime container
FROM alpine

# Copy the compiled firmware into the empty runtime container
COPY --from=buildstep /assets/application.zip /assets/application.zip
