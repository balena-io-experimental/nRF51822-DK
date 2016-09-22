# NUC python base-image
# See more about resin base images here: http://docs.resin.io/runtime/resin-base-images/
FROM resin/nuc-python

# Enable systemd init system
ENV INITSYSTEM on

# Use apt-get to install dependencies
RUN apt-get update && apt-get install -yq \
    binutils-arm-none-eabi \
    gcc-arm-none-eabi \
    libnewlib-arm-none-eabi \
    unzip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Nordic SDK
RUN cd /opt && \
    wget https://developer.nordicsemi.com/nRF51_SDK/nRF5_SDK_v11.x.x/nRF5_SDK_11.0.0_89a8197.zip && \
    mkdir nRF5_SDK_11.0.0_89a8197 && \
    unzip -q nRF5_SDK_11.0.0_89a8197.zip -d nRF5_SDK_11.0.0_89a8197 && \
    rm nRF5_SDK_11.0.0_89a8197.zip && \
    sed -i 's|/local/gcc-arm-none-eabi-4_9-2015q1||g' /opt/nRF5_SDK_11.0.0_89a8197/components/toolchain/gcc/Makefile.posix

# Install nrfutil
RUN cd /opt && \
    git clone https://github.com/NordicSemiconductor/pc-nrfutil.git && \
    cd pc-nrfutil && \
    git checkout 0_5_1 && \
    pip install -r requirements.txt && \
    python setup.py install

# Set the working directory
WORKDIR /usr/src/app

# If the firmware is already compiled copy it to /assets
# COPY application.zip /assets

# If the firmware is not already compiled...
# Copy all files to the working directory in the container
COPY . ./

# Compile the firmware
RUN make

# Move the firmware to /assets
RUN mv application.zip /assets