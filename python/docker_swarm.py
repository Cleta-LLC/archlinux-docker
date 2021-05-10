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


if __name__ == "__main__":

    host_list = ["192.168.1.197", "192.168.1.198", "192.168.1.163"]
    host = None
    default_port = 22
    default_username = "alarm"
    default_password = "alarm"
    new_username = "raspi"
    new_password = "ipsar"
    root_password = "root"

    print("System Update for a Archlinux Arm device")
    raspi1 = RaspiSSH(
        host=host_list[0], port=default_port, username=default_username, password=default_password)
    raspi1.add_root_password(root_password)
    # raspi1.start()
    # send_command(raspi1, command="pacman-key --init", permission="su") 
    # raspi1.stop()

    # raspi1.start()
    # send_command(raspi1, command="pacman-key --populate archlinuxarm", permission="su") 
    # raspi1.stop()

    # raspi1.start()
    # send_command(raspi1, command="pacman -Syu --noconfirm", permission="su") 
    # raspi1.stop()

    # raspi1.start()
    # send_command(raspi1, command="pacman -S sudo --noconfirm", permission="su") 
    # raspi1.stop()

    # raspi1.start()
    # send_command(raspi1, command="pacman -Syu base base-devel git vim docker docker-machine --needed networkmanager --noconfirm\n", permission="su") 
    # raspi1.stop()

    # Network Installation
    raspi1.start()
    send_command(raspi1, command="pacman -Syu wpa_supplicant connman bluez openvpn --needed --noconfirm\n", permission="su") 
    send_command(raspi1, command="pacman -Syu wpa_supplicant connman bluez openvpn --needed --noconfirm\n", permission="su") 
    raspi1.stop()


    raspi1.start()
    send_command(raspi1, command="pacman -Syu base base-devel git vim docker docker-machine --needed networkmanager --noconfirm\n", permission="su") 
    raspi1.stop()

    raspi1.start()
    send_command(raspi1, command="systemctl enable docker", permission="su") 
    raspi1.stop()

    raspi1.start()
    send_command(raspi1, command="systemctl start docker", permission="su") 
    raspi1.stop()

    # join_swarm = "docker swarm join --token SWMTKN-1-31qfunuwra6s6kwttpxrihufywoopp1icptp0o9o2geadujm5n-1sb01wbo42z6knai02zlk7z9g 192.168.1.231:2377"

    # for host in host_list:
    #     # Override for testing
    #     new_username = default_username
    #     new_password = default_password

    #     print("Connecting to new user: {}".format(new_username))
    #     config = Config(overrides={'sudo': {'password': new_password}})
    #     c = Connection("{}@{}".format(new_username, host), connect_kwargs={'password':new_password}, config=config)
    #     responder_password = Responder(
    #         pattern=r'\[sudo\] password for raspi: ',
    #         response='{0}\n'.format(new_password),
    #     )
    #     print("Connected to user: ", end="")
    #     c.run('whoami')

    #     # System update
    #     c.sudo("pacman -Syu base base-devel git vim docker docker-machine --needed networkmanager --noconfirm\n")

    #     c.sudo("pacman -S ntp --needed --noconfirm\n")
    #     c.sudo("ntpd -u ntp:ntp\n")
    #     c.sudo("systemctl enable ntpd.service\n")
    #     c.sudo("systemctl start ntpd.service\n")
    #     c.run("ntpd -p\n")

        # Install programs using yay
        # c.run("git -c http.sslVerify=false clone https://aur.archlinux.org/yay.git\n")
        # c.run("cd yay && makepkg -si --noconfirm\n", pty=True, watchers="responder_password")


    # enable_docker = "systemctl enable docker"
    # start_docker = "systemctl start docker"
    # join_swarm = "docker swarm join --token SWMTKN-1-31qfunuwra6s6kwttpxrihufywoopp1icptp0o9o2geadujm5n-1sb01wbo42z6knai02zlk7z9g 192.168.1.231:2377"


    # print("Command 1:")
    # result = SerialGroup('192.168.1.197', '192.168.1.198', '192.168.1.163').sudo(enable_docker)
    # res_sorted = sorted(result.items())
    # print(res_sorted)

    # print("Command 2:")
    # result = SerialGroup('192.168.1.197', '192.168.1.198', '192.168.1.163').sudo(start_docker)
    # res_sorted = sorted(result.items())
    # print(res_sorted)

    # print("Command 3:")
    # result = SerialGroup('192.168.1.197', '192.168.1.198', '192.168.1.163').sudo(start_docker)
    # res_sorted = sorted(result.items())
    # print(res_sorted)

