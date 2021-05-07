#!/bin/bash

export DOWNLOADDIR=/tmp/archlinuxarm
export RASPBERRY=false
export I3_GUI=true
export PACKAGES=(ESSENTIALPKGS RASPBERRYPGS FULLPKGS)

# Initialize the archlinux arm keyring, but discard any private key that may be shipped.
pacman-key --init
pacman -Syu --noconfirm
pacman-key --populate archlinuxarm
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

# OVERRIDE PACKAGES FOR TESTING
PACKAGES=/essentialpackages
I3_GUI=true


# Docker File Starts
From scratch

# Initialize the archlinux arm keyring, but discard any private key that may be shipped.
RUN pacman-key --init && pacman-key --populate archlinuxarm && rm -rf etc/pacman.d/gnupg/{openpgp-revocs.d/,private-keys-v1.d/,pubring.gpg~,gnupg.S.}*

# Update pacman
RUN pacman -Syu --noconfirm

ENV LANG=en_US.UTF-8
CMD ["/usr/bin/bash"]


# Pacman Stuff
yay -S reflector
sudo reflector --latest 100 --protocol http --protocol https --sort rate --save /etc/pacman.d/mirrorlist
# TODO add color to pacman by enabling color on /etc/pacman.conf (copy that file)

echo "Restoring user preferences"
mkdir -p ~/Data/Git/
cd ~/Data/Git/
git clone https://github.com/sdmunozsierra/dotfiles.git
cd dotfiles/config/
cp -r . ~/

echo "Installing all programs"
cd ..
cd ArchScripts/
# Packages from workpkglist.txt
while read line
do
    yay -S --noconfirm --needed $line
done < workpkglist.txt

echo "Applying config"
cd ~/
source .bashrc
source .bash_aliases

echo "Installing Vim plugins"
git clone https://github.com/VundleVim/Vundle.vim.git ~/.vim/bundle/Vundle.vim
vim +PluginInstall +qall
cd ~/.vim/bundle/YouCompleteMe
sh ./install.py --all

echo "finished"