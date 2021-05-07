"""Use paramiko to install Arch Linux base."""
from socket import timeout
import time
import paramiko
from paramiko.channel import Channel
from paramiko.ssh_exception import AuthenticationException

def install_base(host, username, port, password, root_password="root"):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, port, username, password)
        channel:Channel = ssh.invoke_shell()
        channel_data = str()
        while True:
            channel_data += str(channel.recv(999))

            
            print("Using SU")
            channel.send("su -\n")
            time.sleep(1)
            #if Password in channel_data
            channel.send(root_password + "\n")
            time.sleep(3)

            # print("Init pacman")
            channel.send("pacman-key --init\n")
            time.sleep(3)

            # print("Populate pacman")
            channel.send("pacman-key --populate archlinxarm\n")
            time.sleep(5)

            # print("Update pacman... 6 minutes")
            channel.send("pacman -Syu --noconfirm\n")
            time.sleep(360)

            # print("Install sudo")
            channel.send("pacman -S sudo --noconfirm\n")
            time.sleep(5)

            # uncomment sudoers
            print("Uncomment wheel")
            channel.send("echo $'\n%wheel ALL=(ALL) ALL' >> /etc/sudoers\n")


            channel_data += str(channel.recv(99999))
            print("Pacman Install Complete + Sudo!")
            print(channel_data)

            # Set groups
            print("Setting sudoers")
            channel.send("useradd -m -g users -G wheel -s /bin/bash {}\n".format(username))
            time.sleep(2)
            channel.send("passwd {}\n".format(username))
            time.sleep(1)
            channel.send("toor\n")  # first
            time.sleep(2)
            channel.send("toor\n")  # confirm
            time.sleep(1)

            print("Exiting super user")
            channel.send("exit\n")
            time.sleep(3)

            print("Activating sudo for new user. Sudo password input")
            channel.send("su archnode\n")
            time.sleep(3)
            channel.send("toor" + "\n")
            time.sleep(3)
            channel_data = str(channel.recv(99999))
            print("User setup complete")
            print(channel_data)
            # channel.send("reboot\n")
            channel.close()
            ssh.close()
            break

    except (timeout, AuthenticationException):
        print("Could not connect to host")

def setup_user(host, username, port, password, root_password="root"):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, port, username, password)
        channel:Channel = ssh.invoke_shell()
        channel_data = str()

        while True:
            channel_data += str(channel.recv(999))

            # first user login
            print("Activating sudo for new user")
            print("Sudo password input")
            channel.send("sudo -i\n")
            time.sleep(2)
            print("Current user password: {}".format(password))
            channel.send(password + "\n")
            time.sleep(4)
            #channel.send("userdel alarm\n")

            channel_data = str(channel.recv(99999))
            print("New user setup complete")
            print(channel_data)
            channel.close()
            ssh.close()
            break


    except (timeout, AuthenticationException):
        print("Could not connect to host")


if __name__ == '__main__':
    host = "192.168.1.243"
    user = "alarm"
    port = 22
    password = "alarm"
    # install_base(host, user, port, password)
    time.sleep(10)

    host = "192.168.1.243"
    user = "archnode"
    port = 22
    password = "toor"
    setup_user(host, user, port, password)