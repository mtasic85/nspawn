import os
import sys
import random
import hashlib
import argparse

import yaml


def machine_list():
    if not os.path.exists('machines.yaml'):
        with open('machines.yaml', 'w'):
            pass

    with open('machines.yaml', 'r') as f:
        machines = yaml.load(f)
        
        if not machines:
            machines = []

    print('{a: <40} {b: <39}'.format(a='ID', b='Remote Address'))
    print('{} {}'.format('-' * 40, '-' * 39))

    for machine_id, machine_remote_address in machines:
        print('{a: <40} {b: <39}'.format(a=machine_id, b=machine_remote_address))

    print('{} {}'.format('-' * 40, '-' * 39))

def machine_add(remote_address):
    if not os.path.exists('machines.yaml'):
        with open('machines.yaml', 'w'):
            pass

    with open('machines.yaml', 'r') as f:
        machines = yaml.load(f)
        
        if not machines:
            machines = []

    # check if remote_address already exists
    for machine_id, machine_remote_address in machines:
        if remote_address == machine_remote_address:
            print('Machine with remote address {} already exists'.format(remote_address))
            sys.exit(1)

    # generate random ID
    m = hashlib.sha1()
    m.update('{}'.format(random.randint(0, 2 ** 128)).encode())
    id_ = m.hexdigest()

    machine = (id_, remote_address)
    machines.append(machine)

    with open('machines.yaml', 'w') as f:
        machines = yaml.safe_dump(machines, f)


def machine_remove():
    pass


def container_list():
    pass


def container_add():
    pass


def container_remove():
    pass


def container_start():
    pass


def container_stop():
    pass


def container_restart():
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='systemd-nspawn deployment')
    parser_subparsers = parser.add_subparsers(dest='subparser', metavar='main')
    
    # machine
    machine_parser = parser_subparsers.add_parser('machine')
    machine_subparsers = machine_parser.add_subparsers(dest='machine_subparser', metavar='machine')
    
    # machine list
    machine_list_parser = machine_subparsers.add_parser('list', help='List machines')
    # machine_list_parser.add_argument('remote_address', help='HOST:PORT, where port is 22 by default')
    
    # machine add
    machine_add_parser = machine_subparsers.add_parser('add', help='Add machine')
    machine_add_parser.add_argument('remote_address', help='HOST:PORT, where port is 22 by default')

    # machine remove
    machine_remove_parser = machine_subparsers.add_parser('remove', help='Remove machine')
    machine_remove_parser.add_argument('remote_address', help='HOST:PORT, where port is 22 by default')
    
    # container 
    container_parser = parser_subparsers.add_parser('container')
    container_subparsers = container_parser.add_subparsers(dest='container_subparser', metavar='container')
    
    # container list
    container_list_parser = container_subparsers.add_parser('list', help='List of containers at remote host')
    # container_list_parser.add_argument('remote_address', help='HOST:PORT, where port is 22 by default')

    # parse args
    args = parser.parse_args()
    print(args)

    if args.subparser == 'machine':
        if args.machine_subparser == 'list':
            machine_list()
        elif args.machine_subparser == 'add':
            machine_add(args.remote_address)
        elif args.machine_subparser == 'remove':
            machine_remove()
    elif args.subparser == 'container':
        if args.container_subparser == 'list':
            container_list()
