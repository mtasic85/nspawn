# Introduction
nspawn-deploy is simple systemd-nspawn deployment utility.

Basic idea is to allow running containers across clusters of servers.

Communication between local machine and cluster of servers (also known as nodes) has to be secure by design. For this reason we use SSH for all communication between all nodes in system. 


# Remote servers

Arch Linux post-install requires:
```
# pacman-key --init
# pacman-key --populate archlinux
# pacman-key --refresh-keys
```

## SSH

You will need to know all servers addresses, and they all need to have SSH server running on each remote server.

## Users

Create user 'dcloud'.

## sudo

Make sure user 'dcloud' does not require password for sudo.


# Local machine

## Generate private and public SSH keys

Make sure you have valid RSA keys generated, if not run this command:

```
$ ssh-keygen -t rsa
```

## Copy local public SSH key to remote server

Next step is to copy local public SSH key to each remote server. Lets say that remote server behind 192.168.0.150 has user "dcloud".

```
$ ssh-copy-id dcloud@192.168.0.150
```

Or using:

```
$ cat ~/.ssh/id_rsa.pub | ssh dcloud@192.168.0.150 'cat >> .ssh/authorized_keys'
```

## Test SSH connection from local machine to remote server
Now, lets test if we can connect without typing password.

```
$ ssh dcloud@192.168.0.150
```

If you could connect to remote server without typing password, everything is good. Otherwise, please check your SSH keys, and try to copy them from local machine to remote server.

