"""Use paramiko to install Arch Linux base."""
from socket import timeout
import time
import paramiko
from paramiko.channel import Channel
from paramiko.ssh_exception import AuthenticationException

class RaspiSSH():

    def __init__(self, host, port, username, password=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.root_password = None
        self.ssh = self._setup_ssh_connection()
        self.channel = None
        self.data = None
    
    def _setup_ssh_connection(self):
        print("Setting up SSH with paramiko")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        return ssh
    
    def add_password(self, password):
        self.password = password
    
    def add_root_password(self, root_password):
        self.root_password = root_password

    def connect_channel(self):
        print("Setting up a SSH connection")
        if not self.password:
            print("password is required to create a ssh connection.")
            print("Set a password using add_password().")
        try:
            self.ssh.connect(self.host, self. port, self.username, self.password)
            self.channel:Channel = self.ssh.invoke_shell()
        except (timeout, AuthenticationException):
            print("Could not connect to host")
            exit(-1)
    
    def _obtain_su(self):
        print("Using super user SU")
        self.channel.send("su -\n")
        time.sleep(1)
        self.channel.send("\n".format(self.root_password))
        time.sleep(2)

    def _send_command(self, command, time_override=5, su=False, sudo=False):
        if su and sudo:
            print("Only use one super user command [su | sudo]")
            return -1
        if su:
            print("Sending a super user su command")
            self._obtain_su()
            if isinstance(command, list):
                for c in command:
                    self.channel.send("{}\n".format(command))
                    time.sleep(time_override)
            else:
                self.channel.send("{}\n".format(command))
                time.sleep(time_override)
            print("Terminating su session")
            self.channel.send("{}\n".format("exit"))
        elif sudo:
            print("Sending a sudo command")
            print("Not implemented yet")
        else:
            print("Sending a command")
            if isinstance(command, list):
                for c in command:
                    self.channel.send("{}\n".format(command))
                    time.sleep(time_override)
            else:
                self.channel.send("{}\n".format(command))
                time.sleep(time_override)
        if not self.data:
            self.data = ""
        self.data += str(self.channel.recv(999999))

    def execute(self, command=None, time_override=5, su=False, sudo=False):
        if not command:
            print("Send a command to a Raspberry Pi through SSH")
        print("Sending command: {}, waiting for {} seconds".format(command, time_override))
        self._send_command(command, time_override, su, sudo)
        print(self.data)

    def example_command(self, command="whoami"):
        self.execute(command=command)
    

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