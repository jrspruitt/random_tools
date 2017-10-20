#!/bin/bash
# Sets up an environment with cross compiling kernel env vars set.
# run ./cc_kernel_env.sh

export ARCH=arm

# Raspberry Pi Specific.
# export KERNEL=kernel7

export PATH=$PATH:/path/to/toolchain/bin

# Specific to your situation/board/toolchain.
export CROSS_COMPILE=arm-linux-gnueabihf-

# Where do you want kernel modules installed?
export INSTALL_MOD_PATH=path/to/linux_modules

# Creates an environment, exit to get out.
if [ "${BUILDSHELL}" != "1" ]; then
	echo "buildshell"
	export BUILDSHELL=1
	/bin/bash
else
	echo "already there!"
fi

