#!/bin/bash

export DOWNLOADDIR=/tmp/archlinuxarm
export RASPBERRY=true
# export I3_GUI=true
# export PACKAGES=(ESSENTIALPKGS RASPBERRYPGS FULLPKGS)

# Initialize the archlinux arm keyring, but discard any private key that may be shipped.
pacman-key --init
pacman-key --populate archlinuxarm
pacman -Syu --noconfirm
rm -rf etc/pacman.d/gnupg/{openpgp-revocs.d/,private-keys-v1.d/,pubring.gpg~,gnupg.S.}*
# Update the system using pacman
RUN pacman -Syu --noconfirm

# Install basic programs
pacman -Sy --noconfirm --needed base-devel git

# Change the Kernel
pacman -R --noconfirm linux-aarch64 uboot-raspberrypi
pacman -S --noconfirm linux-raspberrypi4
sed -i 's/mmcblk1/mmcblk0/' /etc/fstab

# Install libarchive
cd ${DOWNLOADDIR} && \
wget https://www.libarchive.org/downloads/libarchive-3.3.1.tar.gz
tar xzf libarchive-3.3.1.tar.gz
tar -xvf libarchive-3.3.1
pushd ${DOWNLOADDIR}/libarchive-3.3.1
./configure
make
make install
popd
# clean
rm -rf ${DOWNLOADDIR}/libarchive-3.3.1

# Install yay
cd ${DOWNLOADDIR} && \
git clone https://aur.archlinux.org/yay.git
pushd ${DOWNLOADDIR}/yay
makepkg -si --needed --noconfirm
popd
# clean
rm -rf ${DOWNLOADDIR}/yay

# OVERRIDE PACKAGES FOR TESTING
#PACKAGES=/essentialpackages
#I3_GUI=true

# Continue in python