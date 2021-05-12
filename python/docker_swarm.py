from fabric import Connection, Config, SerialGroup
from invoke import Responder
from RaspiSSH import RaspiSSH

def send_command(raspi, command="pacman -S sudo", permission="su"):
    if not isinstance(raspi, RaspiSSH):
        print("RaspiSSH class only")
        exit(-1)

    if permission == "su":
        config = Config(overrides={'sudo': {'password': raspi.password}})
        c = Connection("{}@{}".format(raspi.username, raspi.host), connect_kwargs={'password':raspi.password}, config=config)
        if not raspi.root_password:
            c.close()
            raspi.stop()
            raspi.close_ssh()
            print("Please add root password")
            exit(-1)

        responder = Responder(pattern=r'Password: ', response='{0}\n'.format(raspi.root_password),)
        c.run("su -c \"{0}\" root\n".format(command), pty=True, watchers=[responder])
    if permission == "sudo":
        responder = Responder(pattern=r'\[sudo\] password for*',
            response='{0}\n'.format(raspi.password),)
        c.sudo("{0}\n".format(command))
        
    c.close()

def system_update(raspi, permission="sudo"):
    if not isinstance(raspi, RaspiSSH):
        print("RaspiSSH class only")
        exit

    config = Config(overrides={'sudo': {'password': raspi.password}})
    c = Connection("{}@{}".format(raspi.username, raspi.host), connect_kwargs={'password':raspi.password}, config=config)
    if not raspi.root_password:
        c.close()
        raspi.stop()
        raspi.close_ssh()
        print("Please add root password")
        exit(-1)
    #responder = create_responder(raspi.root_password, permission="su")

    responder = Responder(
        pattern=r'Password: ',
        response='{0}\n'.format(raspi.root_password),
    )

    if permission == "sudo":
        c.sudo("pacman -Syu --noconfirm\n")
        responder = Responder(pattern=r'\[sudo\] password for*',
            response='{0}\n'.format(raspi.root_password),)
    if permission == "su":
        c.run("su -c \"pacman -Syu --noconfirm\" root\n", pty=True, watchers=[responder])
    c.close()


def pacman_init(device):
    device.start()
    send_command(device, command="pacman-key --init", permission="su") 
    device.stop()

    device.start()
    send_command(device, command="pacman-key --populate archlinuxarm", permission="su") 
    device.stop()

def pacman_update(device):
    device.start()
    send_command(device, command="pacman -Syu --noconfirm", permission="su") 
    device.stop()

def pacman_install_sudo(device):
    device.start()
    send_command(device, command="pacman -S sudo --noconfirm", permission="su") 
    device.stop()

def pacman_install_base(device):
    device.start()
    send_command(device, command="pacman -Syu base base-devel git vim docker docker-machine networkmanager --needed --noconfirm\n", permission="su") 
    device.stop()

def pacman_install_network(device):
    device.start()
    send_command(device, command="pacman -Syu dhcpcd wpa_supplicant connman bluez openvpn --needed --noconfirm\n", permission="su") 
    device.stop()

def pacman_install_secure(device):
    device.start()
    send_command(device, command="pacman -Syu gnome-keyring seahorse pass --needed --noconfirm\n", permission="su") 
    device.stop()

def setup_firewall(device):
    device.start()
    send_command(device, command="pacman -Syu gnome-keyring seahorse pass --needed --noconfirm\n", permission="su") 
    device.stop()

def pacman_install_bash_completion(device):
    device.start()
    send_command(device, command="pacman -S bash-completion --noconfirm --needed", permission="su") 
    device.stop()

    device.start()
    send_command(device, command="sed -e '/unset -f have s/^#*/#/' -i /usr/share/bash-completion/bash_completion",
     permission="su") 
    device.stop()

    device.start()
    send_command(device, command="sed -e '/unset have s/^#*/#/' -i /usr/share/bash-completion/bash_completion",
     permission="su") 
    device.stop()

    device.start()
    send_command(device, command='cat /usr/share/bash-completion/bash_completion | grep "unset have -f" -A 1',
     permission="su") 
    device.stop()

def docker_setup(device):
    device.start()
    send_command(device, command="pacman -Syu docker docker-machine --needed --noconfirm\n", permission="su") 
    device.stop()

    device.start()
    send_command(device, command="systemctl enable docker", permission="su") 
    device.stop()

    device.start()
    send_command(device, command="systemctl start docker", permission="su") 
    device.stop()
    
    device.start()
    print("Adding current user to docker group")
    send_command(device, command="usermod -aG docker ".format(device.username), permission="su") 
    device.stop()

def docker_join_swarm(device):
    join_swarm = "docker swarm join --token SWMTKN-1-31qfunuwra6s6kwttpxrihufywoopp1icptp0o9o2geadujm5n-1sb01wbo42z6knai02zlk7z9g 192.168.1.231:2377"
    device.start()
    send_command(device, command=join_swarm, permission="su") 
    device.stop()

def install_yay(device):
    # c.run("git -c http.sslVerify=false clone https://aur.archlinux.org/yay.git\n")
    # c.run("cd yay && makepkg -si --noconfirm\n", pty=True, watchers="responder_password")
    pass

def setup_date_time(device):
    device.start()
    send_command(device, command="pacman -S npt --needed --noconfirm", permission="su") 
    device.stop()

    device.start()
    send_command(device, command='timedatectl set-time "{}"'.format(), permission="su") 
    device.stop()

    device.start()
    send_command(device, command="hwclock --systohc --utc", permission="su") 
    device.stop()

    device.start()
    send_command(device, command="systemctl enable sytemd-timesyncd", permission="su") 
    device.stop()

    device.start()
    send_command(device, command="systemctl start sytemd-timesyncd", permission="su") 
    device.stop()

    device.start()
    send_command(device, command="iptables -A INPUT -p udp --destination-port 123 -j ACCEPT", permission="su") 
    device.stop()

if __name__ == "__main__":

    # List of raspberry hosts to perform operations
    host_list = ["192.168.1.197", "192.168.1.198", "192.168.1.163"]
    host_list = ["192.168.1.2"]
    host = None
    default_port = 22
    default_username = "alarm"
    default_password = "alarm"
    root_password = "root"

    new_username = "raspi"  # new user to be created
    new_password = "ipsar"  # new password to be used
    delete_default_username = False # Set to true to delete alarm user !warning!


    # Set up fresh device of type Raspberry Pi through ssh.
    device = RaspiSSH(
        host=host_list[0], port=default_port, username=default_username, password=default_password)
    print(f"Connected to Device: %s", device.username)
    device.add_root_password(root_password)
    print(f"Added root password to Device: %s", device.username)

    pacman_init(device)
    pacman_update(device)
    pacman_install_sudo(device)
    pacman_install_base(device)
    pacman_install_network(device)
    pacman_install_bash_completion(device)

    # SerialGroup is offered but we can use a multiprocessing ourselves.
    # result = SerialGroup('192.168.1.197', '192.168.1.198', '192.168.1.163').sudo(enable_docker)
    # res_sorted = sorted(result.items())
    # print(res_sorted)
