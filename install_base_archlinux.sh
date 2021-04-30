#!/bin/bash

export DOWNLOADDIR=/tmp/archlinux

# Initialize the archlinux keyring, but discard any private key that may be shipped.
pacman-key --init
pacman-key --populate archlinux
pacman -Syu --noconfirm
rm -rf etc/pacman.d/gnupg/{openpgp-revocs.d/,private-keys-v1.d/,pubring.gpg~,gnupg.S.}*
# Update the system using pacman
RUN pacman -Syu --noconfirm

# Install basic programs
pacman -Sy --noconfirm --needed base-devel git

# Install libarchive
wget https://www.libarchive.org/downloads/libarchive-3.3.1.tar.gz
tar xzf libarchive-3.3.1.tar.gz
tar -xvf libarchive-3.3.1
cd libarchive-3.3.1
./configure
make
make install

# Install yay
cd ${DOWNLOADDIR} && \
git clone https://aur.archlinux.org/yay.git
pushd ${DOWNLOADDIR}/yay
makepkg -si --needed --noconfirm
popd
rm -rf ${DOWNLOADDIR}/yay