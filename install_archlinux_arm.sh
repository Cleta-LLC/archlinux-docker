#!/bin/bash

# First Boot
# Connect your raspberry and connect it to the ethernet cable. Then SSH into your device:

Find your raspi device
sudo nmap -sn 192.168.X.X/24
ssh alarm@192.168.X.XXX

# Develop a python script

## Send commands to all available pi's

Populate Pacman
pacman-key --init
pacman-key --populate archlinuxarm
pacman -Syu --noconfirm

Change the Kernel
pacman -R --noconfirm linux-aarch64 uboot-raspberrypi
pacman -S --noconfirm linux-raspberrypi4

sed -i 's/mmcblk1/mmcblk0/' /etc/fstab

#Check that USB Devices are working
dmesg|grep "xhci_hcd"

# Setup SSDs
# Install two ssd drives into the raspberry pi and do the following

# Install gdisk

pacman -Sy gptfdisk

# Use it to partition both hard drives. Default values are OK since

# we want to create a single partition as big as the whole hard drives

gdisk /dev/sda

# Now create a single partition as big as the drive

# Type n then p.

# Accepts the defaults for every following question.

# Type w to write and exit

gdisk /dev/sdb

# Do the same exact procedure of above

# We created /dev/sda1 and /dev/sdb1 partitions

# Create an ext4 filesystem on these partitions

mkfs.ext4 /dev/sda1
mkfs.ext4 /dev/sdb1

# mdadm --create --verbose --level=10 --metadata=1.2 --chunk=512 --raid-devices=2 --layout=f2 /dev/md/MyRAID10Array /dev/sdb1/dev/sdc1

mkfs.ext4 /dev/md0

Add in /etc/fstab
/dev/md0 /home ext4 defaults,nofail 0 0

Modify /etc/mdadm.conf
MAILADDR raspi-ethnode@support.cleta.io

# Add Basic Programs and Settings
pacman -S hdparm vim sudo

# User Setup
useradd -m -g users -G wheel -s /bin/bash ethnode
passwd ethnode
visudo -> uncomment %wheel
userdel alarm
reboot

# Install libarchive
wget https://www.libarchive.org/downloads/libarchive-3.3.1.tar.gz
tar xzf libarchive-3.3.1.tar.gz
tar -xvf libarchive-3.3.1
cd libarchive-3.3.1
./configure
make
make install

# Ethereum Install
pacman -S geth

Create the service file /etc/systemd/system/geth@.service with the following content:
[Unit]Description=geth Ethereum daemon
Requires=network.target[Service]Type=simple
User=%I
ExecStart=/usr/bin/geth --syncmode light --cache 64 --maxpeers 12
Restart=on-failure

[Install]WantedBy=multi-user.target
--maxpeers default value is 25

# Start the service:
systemctl enable geth@geth.service
systemctl start geth@geth.service

# Attach a process:
geth attach

# Security Measures
# Modify /etc/sudoers using visudo
# Defaults rootpw
# Defaults insults # Haha
# Now lock the sudo account.
# sudo passwd -l root
# A similar command unlocks root.
# $ sudo passwd -u root
# Alternatively, edit /etc/shadow and replace the root's encrypted password with "!":
# root:!:12345::::::
# To enable root login again:
# $ sudo passwd root

# SSD installation
sudo chmod 775 /mnt