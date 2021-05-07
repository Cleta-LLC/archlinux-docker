import getpass
from fabric import Connection, Config
from invoke import Responder, watchers


if __name__ == "__main__":
    print("hello world from main")
    #sudo_pass = getpass.getpass("Sudo password:")
    #config = Config(overrides={'sudo': {'password': password}})

    # Create dict with hostname and ip address
    fullhost = "alarm@192.168.1.243"
    user = "alarm"
    host = "192.168.1.243"
    port = 22
    password = "alarm"
    sudo_password = "root"

    # Create a connection with the default Alarm user and password
    c = Connection("alarm@192.168.1.243", connect_kwargs={'password':password})
    # c = Connection(host, user, port, connect_kwargs={'password':password}) # Same as above

    c.run('whoami')

    # Create a responder that will set up the Super User password 
    responder_su = Responder(
        pattern=r'Password:',
        response='root\n',
    )

    # Get Super User privileges
    #c.run('su', pty=True, watchers=[responder_su])  # Now a superuser

    # Create a responder that will set up the sudo password 
    responder_su = Responder(
        pattern=r'\[sudo\] password for *:',  # you can specify the username for more security
        response='alarm\n',
    )

    # Run sudo commands
    c.run('sudo whoami', pty=True, watchers=[responder_su])


    # Transpose bash script to be understandable by python
    # 0. Super User setup the keyring
    # 1. install sudo
    # Use paramiko directly
    # 2. Set Users & groups
    # Use paramiko directly

    # 3. `Disable` root user

    # 4. Setup yay
    # Create a new connection with new user
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

    # Change the kernel if not already
    # c.sudo("pacman -R linux-arch64 uboot-raspberrypi --noconfirm\n")
    # c.sudo("pacman -S linux-raspberrypi4 --noconfirm\n")

    # 5. Setup OBS

