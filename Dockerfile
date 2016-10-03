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

# Make the /assets directory
RUN mkdir -p /assets

# Set the working directory
WORKDIR /usr/src/app

# Copy all files to the working directory in the container
COPY . ./

# Compile the firmware
RUN make

# Move the firmware to /assets/
RUN mv application.zip /assets/

# Below we try to reduce the image size as much as possible to speed up the
# development cycle

# Remove packages
RUN apt-get purge --auto-remove -yq \
binutils-arm-none-eabi \
gcc-arm-none-eabi \
libnewlib-arm-none-eabi \
unzip

# Remove nRF5_SDK
RUN cd /opt && rm -rf nRF5_SDK_11.0.0_89a8197

# Remove pc-nrfutil
RUN cd /opt && rm -rf pc-nrfutil

# Remove everying from the working directory
RUN rm -rf *
