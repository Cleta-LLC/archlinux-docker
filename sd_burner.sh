#!/bin/bash

# Find which partitions to use automatically. #TODO: #Future #Request

# Installation
# Download and Install Arch
export SDDEV=/dev/sdf
export SDPARTBOOT=/dev/sdf1
export SDPARTROOT=/dev/sdf2
export SDMOUNT=/mnt/sd
export DOWNLOADDIR=/tmp/pi

# Check if user is root or sudo
if ! [ $( id -u ) = 0 ]; then
    echo "Please run this script as sudo or root" 1>&2
    exit 1
fi

mkdir -p $DOWNLOADDIR
(
  cd $DOWNLOADDIR && \
  curl -JLO http://os.archlinuxarm.org/os/ArchLinuxARM-rpi-aarch64-latest.tar.gz
)

sfdisk --quiet --wipe always $SDDEV << EOF
,256M,0c,
,,,
EOF

mkfs.vfat -F 32 $SDPARTBOOT
mkfs.ext4 -q -E lazy_itable_init=0,lazy_journal_init=0 -F $SDPARTROOT

mkdir -p $SDMOUNT
mount $SDPARTROOT $SDMOUNT
mkdir -p ${SDMOUNT}/boot
mount $SDPARTBOOT ${SDMOUNT}/boot

bsdtar -xpf ${DOWNLOADDIR}/ArchLinuxARM-rpi-aarch64-latest.tar.gz -C $SDMOUNT

sed -i 's/mmcblk0/mmcblk1/' ${SDMOUNT}/etc/fstab

# (Optional for Headless Boot) Replace Uboot
mkdir -p ${DOWNLOADDIR}/uboot
pushd ${DOWNLOADDIR}/uboot
curl -JLO http://ports.ubuntu.com/pool/universe/u/u-boot/u-boot-rpi_2020.10+dfsg-1ubuntu0~20.04.2_arm64.deb
ar x *.deb
tar xf data.tar.xz
cp usr/lib/u-boot/rpi_arm64/u-boot.bin ${SDMOUNT}/boot/kernel8.img
popd

# Sync and Umount
sync
umount -R $SDMOUNT
