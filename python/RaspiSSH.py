"""Execute commands in a device running ssh. Compatible with Raspberry Pi 4 running on arch linux arm."""
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
    
    def _flush(self):
        print("Cleaning channel data")
        print(self.data)
        self.data = ""
        time.sleep(2)
        
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
 

class RaspiSSHCommander():

    def __init__(self):
        self.raspi_list = []
        self.size = 0
        self.registry = []
    
    def get_size(self):
        return self.size

    def add_raspi(self, raspi_ssh):
        print("Checking if raspi already on the fleet")
        if not isinstance(raspi_ssh, RaspiSSH):
            print("Currently only Raspberry devices are accepted or extend class RaspiSSH")
            return
        if raspi_ssh not in self.raspi_list:
            self.raspi_list.append(raspi_ssh)
            self.registry.append("raspi{}".format(self.size))
            self.size+=1


    def execute(self, command=None, time_override=5, su=False, sudo=False):
        print("Executing on {} devices".format(self.size))
        for raspberry in self.raspi_list:
            print("Raspberry: ")
            raspberry._flush()
            raspberry.execute(command, time_override, su, sudo)
        

    def populate_pacman(self):
        print("Populating pacman")
        self.execute("pacman-key --init", su=True)
        self.execute("pacman-key --populate archlinuxarm", su=True)

    def update_pacman(self):
        print("Updating pacman")
        self.execute("pacman -Syu --noconfirm", time_override=360, su=True)
    
    def install_sudo(self):
        # Run with su
        print("Installing sudo")
        self.execute("pacman -S sudo --noconfirm", time_override=10, su=True)

        print("Enabling sudoers. Uncommenting wheel")
        self.execute("echo $'\n%wheel ALL=(ALL) ALL' >> /etc/sudoers\n", su=True)

    def set_new_user(self, username="raspi", new_password="ipsar"):
        print("Setting up new user")
        self.execute("useradd -m -g users -G wheel -s /bin/bash {}\n".format(username), 2, True)
        self.execute("passwd {}\n".format(username), 1, True)  # change passwd
        self.execute("{}\n".format(new_password), 2, True)  # first time
        self.execute("{}\n".format(new_password), 2, True)  # confirm passwd

        # As list format
        # execute (
        #     ["useradd -m -g users -G wheel -s /bin/bash {}\n",
        #     "passwd {}\n".format(username),
        #     "{}\n".format(new_password),
        #     "{}\n".format(new_password)], 2, True)

        print("Activate sudo for new user")
        self.execute(["su {}\n".format(username), "{}\n".format(new_password)], 3, True)
