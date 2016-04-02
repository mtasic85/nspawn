import os
import sys
import random
import hashlib
import argparse

import yaml


def machine_list():
    if os.path.exists('machines.yaml'):
        with open('machines.yaml', 'r') as f:
            machines = yaml.load(f)
            
            if not machines:
                machines = {}
    else:
        machines = {}

    print('{a: <12} {b: <67}'.format(a='Machine ID', b='Address'))
    print('{a:-<12} {b:-<67}'.format(a='', b=''))

    for machine_id, machine in machines.items():
        print('{a: <12} {b: <67}'.format(
            a=machine['id'][-12:],
            b=machine['address'],
        ))

    print('{a:-<12} {b:-<67}'.format(a='', b=''))

def machine_add(address):
    # load machines
    if os.path.exists('machines.yaml'):
        with open('machines.yaml', 'r') as f:
            machines = yaml.load(f)
            
            if not machines:
                machines = {}
    else:
        machines = {}

    # check if address already exists
    for machine_id, machine in machines.items():
        if address == machine['address']:
            print('Machine with address {} already exists'.format(address))
            sys.exit(1)

    # generate random ID
    m = hashlib.sha1()
    m.update('{}'.format(random.randint(0, 2 ** 128)).encode())
    machine_id = m.hexdigest()

    machine = {
        'id': machine_id,
        'address': address,
    }

    machines[machine_id] = machine

    # save machines
    with open('machines.yaml', 'w') as f:
        yaml.safe_dump(machines, f)

    print('{}'.format(machine_id))


def machine_remove(machine_id, address):
    if os.path.exists('machines.yaml'):
        with open('machines.yaml', 'r') as f:
            machines = yaml.load(f)
            
            if not machines:
                machines = {}
    else:
        machines = {}

    if machine_id:
        # convert short ID to long ID
        if len(machine_id) == 12:
            for m_id in machines:
                if m_id[-12:] == machine_id:
                    machine_id = m_id
                    break

        if machine_id not in machines:
            print('Machine with id {} does not exists'.format(machine_id))
            sys.exit(1)

        del machines[machine_id]
    else:
        for machine_id, machine in list(machines.items()):
            if machine['address'] == address:
                del machines[machine_id]
                break
        else:
            print('Machine with address {} does not exists'.format(address))
            sys.exit(1)

    with open('machines.yaml', 'w') as f:
        yaml.safe_dump(machines, f)


def container_list():
    # load containers
    if os.path.exists('containers.yaml'):
        with open('containers.yaml', 'r') as f:
            containers = yaml.load(f)
            
            if not containers:
                containers = {}
    else:
        containers = {}

    # load machines
    if os.path.exists('machines.yaml'):
        with open('machines.yaml', 'r') as f:
            machines = yaml.load(f)
            
            if not machines:
                machines = {}
    else:
        machines = {}

    print('{a: <12} {b: <12} {c: <15} {d: <16} {e: <19} {f: <1}'.format(
        a='Container ID',
        b='Machine ID',
        c='Address',
        d='Name',
        e='Ports',
        f='S', # Status
    ))

    print('{a:-<12} {b:-<12} {c:-<15} {d:-<16} {e:-<19} {f:-<1}'.format(
        a='', b='', c='', d='', e='', f=''))

    for container_id, container in containers.items():
        machine_id = container['machine_id']
        machine = machines[machine_id]
        status = 'x'

        print('{a: <12} {b: <12} {c: <15} {d: <16} {e: <19} {f: <1}'.format(
            a=container_id[-12:],
            b=machine_id[-12:],
            c=machine['address'],
            d=container['name'][:18],
            e=container['ports'][:19],
            f=status,
        ))

    print('{a:-<12} {b:-<12} {c:-<15} {d:-<16} {e:-<19} {f:-<1}'.format(
        a='', b='', c='', d='', e='', f=''))


def container_add(machine_id, address, name, ports, distro, image_id, image):
    # load containers
    if os.path.exists('containers.yaml'):
        with open('containers.yaml', 'r') as f:
            containers = yaml.load(f)
            
            if not containers:
                containers = {}
    else:
        containers = {}

    # load machines
    if os.path.exists('machines.yaml'):
        with open('machines.yaml', 'r') as f:
            machines = yaml.load(f)
            
            if not machines:
                machines = {}
    else:
        machines = {}

    if machine_id:
        if machine_id not in machines:
            print('Unknown machine id {}'.format(machine_id))
            sys.exit(1)
    else:
        for machine_id_, machine in machines.items():
            if machine['address'] == address:
                machine_id = machine_id_
                break
        else:
            print('Unknown machine address {}'.format(address))
            sys.exit(1)

    # generate random ID
    m = hashlib.sha1()
    m.update('{}'.format(random.randint(0, 2 ** 128)).encode())
    container_id = m.hexdigest()

    container = {
        'id': container_id,
        'machine_id': machine_id,
        'address': address,
        'name': name,
        'ports': ports,
        'distro': distro,
        'image_id': image_id,
        'image': image,
    }

    containers[container_id] = container

    with open('containers.yaml', 'w') as f:
        yaml.safe_dump(containers, f)

    print('{}'.format(container_id))


def container_remove(container_id):
    # load containers
    if os.path.exists('containers.yaml'):
        with open('containers.yaml', 'r') as f:
            containers = yaml.load(f)
            
            if not containers:
                containers = {}
    else:
        containers = {}

    # convert short ID to long ID
    if len(container_id) == 12:
        for c_id in containers:
            if c_id[-12:] == container_id:
                container_id = c_id
                break

    if container_id not in containers:
        print('Unknown container id {}'.format(container_id))
        sys.exit(1)

    del containers[container_id]

    with open('containers.yaml', 'w') as f:
        yaml.safe_dump(containers, f)


def container_start(container_id):
    pass


def container_stop(container_id):
    pass


def container_restart(container_id):
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='systemd-nspawn deployment')
    parser_subparsers = parser.add_subparsers(dest='subparser', metavar='main')
    
    # machine
    machine_parser = parser_subparsers.add_parser('machine')
    machine_subparsers = machine_parser.add_subparsers(dest='machine_subparser', metavar='machine')
    
    # machine list
    machine_list_parser = machine_subparsers.add_parser('list', help='List machines')
    
    # machine add
    machine_add_parser = machine_subparsers.add_parser('add', help='Add machine')
    machine_add_parser.add_argument('--id', '-I', help='Machine ID')
    machine_add_parser.add_argument('--address', '-a', help='HOST:PORT, where port is 22 by default')

    # machine remove
    machine_remove_parser = machine_subparsers.add_parser('remove', help='Remove machine')
    machine_remove_parser.add_argument('--id', '-I', help='Machine ID')
    machine_remove_parser.add_argument('--address', '-a', help='HOST:PORT, where port is 22 by default')
    
    # container 
    container_parser = parser_subparsers.add_parser('container')
    container_subparsers = container_parser.add_subparsers(dest='container_subparser', metavar='container')
    
    # container list
    container_list_parser = container_subparsers.add_parser('list', help='List of containers at remote host')

    # container add
    container_add_parser = container_subparsers.add_parser('add', help='Add container')
    container_add_parser.add_argument('--machine-id', '-M', help='Machine ID')
    container_add_parser.add_argument('--address', '-a', help='HOST:PORT, where port is 22 by default')
    container_add_parser.add_argument('--name', '-n', help='Human readable name of container')
    container_add_parser.add_argument('--ports', '-p', help='MACHINE_PORT:CONTAINER_PORT[,M_PORT:C_PORT,...]')
    container_add_parser.add_argument('--distro', '-d', default='arch', help='Linux distribution: arch, debian, fedora')
    container_add_parser.add_argument('--image-id', '-I', help='Image ID')
    container_add_parser.add_argument('--image', '-i', help='Image')

    # container remove
    container_remove_parser = container_subparsers.add_parser('remove', help='Remove container')
    container_remove_parser.add_argument('--id', '-I', help='Container ID')

    # parse args
    args = parser.parse_args()
    print(args)

    if args.subparser == 'machine':
        if args.machine_subparser == 'list':
            machine_list()
        elif args.machine_subparser == 'add':
            machine_add(args.address)
        elif args.machine_subparser == 'remove':
            machine_remove(args.id, args.address)
    elif args.subparser == 'container':
        if args.container_subparser == 'list':
            container_list()
        elif args.container_subparser == 'add':
            container_add(args.machine_id, args.address, args.name, args.ports, args.distro, args.image_id, args.image)
        elif args.container_subparser == 'remove':
            container_remove(args.id)
        elif args.container_subparser == 'start':
            container_start(args.id)
        elif args.container_subparser == 'stop':
            container_stop(args.id)
        elif args.container_subparser == 'restart':
            container_restart(args.id)
