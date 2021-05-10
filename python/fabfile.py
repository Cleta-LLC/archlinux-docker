from fabric import Connection, Config
from invoke import Responder, watchers
from RaspiSSH import RaspiSSH
from RaspiSSH import RaspiSSHCommander
import time
import datetime



def test_raspberry_update():
    print("print test raspberry update")

    # Connect one raspberry pi
    raspi1 = RaspiSSH(host="192.168.1.2", port=22, username="alarm", password="alarm")
    raspi1.add_root_password("root")
    raspi1.connect_channel()

    print("Expecting whoami command")
    raspi1.example_command()

    print("Sending populate keys")
    raspi1.example_command(["pacman-key --init", "pacman-key --populate archlinuxarm"], su=True)

    print("Sending update pacman")
    raspi1.example_command(["pacman -Syu --noconfirm"], time_override=360, su=True)

    # Bring the Swarm of Pi's
    # raspi1.create_new_user("raspi01")
    # raspi1.add_new_password("ipsar")


def raspi_bridge():
    """Here work commands that already have the users and groups already set up"""
    # Create dict with hostname and ip address
    fullhost = "alarm@192.168.1.243"
    user = "alarm"
    host = "192.168.1.243"
    port = 22
    password = "alarm"
    sudo_password = "root"

    # Create a connection with the default Alarm user and password
    c = Connection("alarm@192.168.1.243", connect_kwargs={'password':password})
    c.run('whoami')

    # Create a responder that will set up the Super User password 
    responder_su = Responder(
        pattern=r'Password:',
        response='root\n',
    )

    # Create a responder that will set up the sudo password 
    responder_su = Responder(
        pattern=r'\[sudo\] password for *:',  # you can specify the username for more security
        response='alarm\n',
    )

    # Run sudo commands
    c.run('sudo whoami', pty=True, watchers=[responder_su])

    # Finally sudo works as expected...
    config = Config(overrides={'sudo': {'password': 'toor'}})
    c = Connection("archnode@192.168.1.243", connect_kwargs={'password':'toor'}, config=config)
    responder_password = Responder(
        pattern=r'\[sudo\] password for *',
        response='toor\n',
    )
    c.sudo("pacman -S base-devel git --noconfirm\n")
    c.run("git clone https://aur.archlinux.org/yay.git\n")
    c.run("cd yay && makepkg -si --noconfirm\n", pty=True, watchers="responder_password")

    # Install docker-machine
    c.run("yay -S docker-machine --noconfirm\n", pty=True, watchers="responder_password")


def create_docker_swarm():
    # start = time.time()
    # while time.time() - start < 60:
    #     print(datetime.datetime.now().utcnow())
    print("Experiment 2: ")
    print("A commander will send the same command to all added devices")
    commander = RaspiSSHCommander()
    commander.add_raspi(raspi1)
    assert(commander.get_size() == 1)

    print("Expecting whoami command sent to all connected devices:")
    commander.execute("whoami")

def setup_device(device, new_username, new_password):
    if not isinstance(device, RaspiSSH):
        print("Only RaspiSSH")
        exit(-1)

    print("Setting up device: ")

    # Populate Archlinux Arm
    device.start()
    device.execute(["pacman-key --init", "pacman-key --populate archlinuxarm"],
    time_override=10, su=True)
    device.stop()

    # Set new users 
    device.start()
    device.execute(["useradd -m -g users -G wheel -s /bin/bash {}".format(new_username),
     "passwd {}".format(new_username), new_password, new_password], 2, True)
    device.execute("echo {} > /etc/hostname".format(new_username), 2, True)
    device.execute("echo 127.0.0.1 localhost {} >> /etc/hosts".format(new_username), 2, True)
    device.execute("usermod -aG docker {}".format(new_username), 2, True)
    device.stop()

    # Set Locale
    device.start()
    device.execute([
        "ln -s /usr/share/zoneinfo/America/New_York /etc/localtime", 
        'echo "en_US.UTF-8 UTF-8" > /etc/locale.gen', 
        "locale-gen"], su=True)
    device.stop()

    # Set time
    device.start()
    device.execute(["su {}\n".format(new_username), "{}\n".format(new_password)], 2)
    device.execute('echo "LANG=en_US.UTF-8" >> /etc/locale.conf')
    device.execute('echo "LC_COLLATE=C" >> /etc/locale.conf')
    device.execute('echo "LC_TIME=en_US.UTF-8" >> /etc/locale.conf')
    device.stop()

    # Install Sudo
    device.start()
    device.execute(["pacman -S sudo --noconfirm", "echo $'\n%wheel ALL=(ALL) ALL' >> /etc/sudoers\n"],
    time_override=10, su=True)
    device.stop()

    device.stop_ssh()
    print("Device setup complete: ")

if __name__ == "__main__":

    host = "192.168.1.2"
    default_port = 22
    default_username = "alarm"
    default_password = "alarm"
    new_username = "raspi"
    new_password = "ipsar"
    sudo_password = "root"

    print("Setting up Raspberry with Archlinux default credentials:")
    raspi1 = RaspiSSH(host=host, port=default_port, username=default_username, password=default_password)
    raspi1.add_root_password(sudo_password)
    setup_device(raspi1, new_username, new_password)  # Set up a new user named raspi password ipsar

    print("Activating sudo for new user:")
    raspi1 = RaspiSSH(host=host, port=22, username=new_username, password=new_password)
    raspi1.start()
    raspi1.execute(["sudo -i", "{}".format(new_password)], 2)
    raspi1.stop()

    print("Connecting to new user: {}".format(new_username))
    config = Config(overrides={'sudo': {'password': new_password}})
    c = Connection("{}@{}".format(new_username, host), connect_kwargs={'password':new_password}, config=config)

    print("Connected to user: ", end="")
    c.run('whoami')

    # System update
    # System update
    # c.sudo("pacman -Syu base base-devel git vim docker docker-machine --needed networkmanager --noconfirm\n")

    # Install programs using pacman
    # c.sudo("pacman -S ntp --needed --noconfirm\n")
    # c.sudo("ntpd -u ntp:ntp\n")
    # c.sudo("systemctl enable ntpd.service\n")
    # c.run("ntpd -p\n")

    # Install programs using yay
    # c.run("git -c http.sslVerify=false clone https://aur.archlinux.org/yay.git\n")
    # c.run("cd yay && makepkg -si --noconfirm\n", pty=True, watchers="responder_password")

    responder_password = Responder(
        pattern=r'\[sudo\] password for raspi: ',
        response='{0}\n'.format(new_password),
    )
