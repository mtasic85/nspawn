import os
import sys
import json
import shlex
import random
import hashlib
import argparse

import yaml
import paramiko


def load_remote_config(remote_uri, filename='nspawn.yaml'):
    remote_username, remote_address = remote_uri.split('@')
    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    known_hosts_path = os.path.expanduser('~/.ssh/known_hosts')
    client.load_host_keys(known_hosts_path)
    client.connect(remote_address, username=remote_username)
    cmd = 'cat {}'.format(filename)
    stdin, stdout, stderr = client.exec_command(cmd)
    config = {} if stderr.read() else yaml.load(stdout)
    return config


def save_remote_config(remote_uri, config, filename='nspawn.yaml'):
    remote_username, remote_address = remote_uri.split('@')
    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    known_hosts_path = os.path.expanduser('~/.ssh/known_hosts')
    client.load_host_keys(known_hosts_path)
    client.connect(remote_address, username=remote_username)
    _config = shlex.quote(yaml.dump(config))
    cmd = 'echo {} > {}'.format(_config, filename)
    stdin, stdout, stderr = client.exec_command(cmd)

    if stderr.read():
        raise IOError


def merge_remote_configs(configs):
    merged_machines = {}
    merged_projects = {}
    merged_containers = {}

    for config in configs:
        # merge machines
        machines = config.get('machines', {})
        merged_machines.update(machines)

        # merge projects
        projects = config.get('projects', {})
        merged_projects.update(projects)

        # merge containers
        containers = config.get('containers', {})
        merged_containers.update(containers)

    config = {
        'machines': merged_machines,
        'projects': merged_projects,
        'containers': merged_containers,
    }

    return config


def load_consensus_config(remote_uri, filename='nspawn.yaml'):
    remote_username, remote_address = remote_uri.split('@')
    configs = []
    config = load_remote_config(remote_uri)
    machines = config.get('machines', {})

    for machine_id, machine in machines.items():
        machine_uri = '{}@{}'.format(machine['user'], machine['address'])
        config = load_remote_config(machine_uri)
        configs.append(config)

    config = merge_remote_configs(configs)
    return config


def save_consensus_config(config, filename='nspawn.yaml'):
    machines = config.get('machines', {})
    
    for machine_id, machine in machines.items():
        try:
            machine_uri = '{}@{}'.format(machine['user'], machine['address'])
            save_remote_config(machine_uri, config)
        except Exception as e:
            err = 'Error saving config on {} with machine id {}.'.format(
                machine['address'],
                machine_id,
            )

            print(err, file=sys.stderr)


#
# machine
#
def machine_list(remote_uri):
    remote_config = load_consensus_config(remote_uri)
    machine_items = remote_config.get('machines', {}).items()
    machine_items = list(machine_items)
    machine_items = sorted(machine_items, key=lambda n: n[1]['address'])
    print('{a: <12} {b: <67}'.format(a='MACHINE_ID', b='ADDRESS'))

    for machine_id, machine in machine_items:
        print('{a: <12} {b: <67}'.format(
            a=machine['id'][-12:],
            b='{}@{}'.format(machine['user'], machine['address']),
        ))


def machine_add(remote_uri, uri):
    remote_username, remote_address = remote_uri.split('@')
    username, address = uri.split('@')
    config = load_consensus_config(remote_uri)
    machines = config['machines']

    # check if address already exists
    for machine_id, machine in machines.items():
        if address == machine['address']:
            msg = 'Machine with address {} already exists'.format(address)
            print(msg, file=sys.stderr)
            sys.exit(1)

    # generate random ID
    m = hashlib.sha1()
    m.update('{}'.format(random.randint(0, 2 ** 128)).encode())
    machine_id = m.hexdigest()

    machine = {
        'id': machine_id,
        'user': username,
        'address': address,
    }

    machines[machine_id] = machine
    save_consensus_config(config)
    print('{}'.format(machine_id))


def machine_remove(remote_uri, machine_id):
    remote_username, remote_address = remote_uri.split('@')
    username, address = uri.split('@')
    config = load_consensus_config(remote_uri)
    machines = config['machines']

    # convert short ID to long ID
    if len(machine_id) == 12:
        for m_id in machines:
            if m_id[-12:] == machine_id:
                machine_id = m_id
                break

    if machine_id not in machines:
        msg = 'Machine with id {} does not exists'.format(machine_id)
        print(msg, file=sys.stderr)
        sys.exit(1)

    del machines[machine_id]
    save_consensus_config(config)
    print('{}'.format(machine_id))


#
# project
#
def project_list(remote_uri):
    remote_config = load_consensus_config(remote_uri)
    project_items = remote_config.get('projects', {}).items()
    project_items = list(project_items)
    project_items = sorted(project_items, key=lambda n: n[1]['name'])
    print('{a: <12} {b: <67}'.format(a='PROJECT_ID', b='NAME'))

    for project_id, project in project_items:
        print('{a: <12} {b: <67}'.format(
            a=project['id'][-12:],
            b='{}'.format(project['name']),
        ))


def project_add(remote_uri, project_name):
    remote_username, remote_address = remote_uri.split('@')
    config = load_consensus_config(remote_uri)
    projects = config['projects']

    # check if project name already exists
    for project_id, project in projects.items():
        if project_name == project['name']:
            msg = 'Project with name {} already exists'.format(project_name)
            print(msg, file=sys.stderr)
            sys.exit(1)

    # generate random ID
    m = hashlib.sha1()
    m.update('{}'.format(random.randint(0, 2 ** 128)).encode())
    project_id = m.hexdigest()

    project = {
        'id': project_id,
        'name': project_name,
    }

    projects[project_id] = project
    save_consensus_config(config)
    print('{}'.format(project_id))


def project_remove(remote_uri, project_id):
    remote_username, remote_address = remote_uri.split('@')
    username, address = uri.split('@')
    config = load_consensus_config(remote_uri)
    projects = config['projects']

    # convert short ID to long ID
    if len(project_id) == 12:
        for p_id in projects:
            if p_id[-12:] == project_id:
                project_id = p_id
                break

    if project_id not in projects:
        msg = 'Project with id {} does not exists'.format(project_id)
        print(msg, file=sys.stderr)
        sys.exit(1)

    del projects[project_id]
    save_consensus_config(config)
    print('{}'.format(project_id))


#
# container
#
def container_list(remote_uri, project_id):
    remote_config = load_consensus_config(remote_uri)
    container_items = remote_config.get('containers', {}).items()
    container_items = [n for n in container_items if n[1]['project_id'].endswith(project_id)]
    container_items = sorted(container_items, key=lambda n: n[1]['name'])
    
    print('{a: <12} {b: <10} {c: <15} {d: <33} {e: <6}'.format(
        a='CONTAINER_ID',
        b='NAME',
        c='ADDRESS',
        d='PORTS',
        e='STATUS',
    ))

    for container_id, container in container_items:
        status = 'x'

        print('{a: <12} {b: <10} {c: <15} {d: <33} {e: <6}'.format(
            a=container_id[-12:],
            b=container['name'][:10],
            c=container['address'],
            d=container['ports'][:33],
            e=status,
        ))


def container_add(remote_uri, project_id, uri, name, ports, distro, image_id, image):
    remote_username, remote_address = remote_uri.split('@')
    config = load_consensus_config(remote_uri)
    containers = config['containers']

    # check if project id exists
    projects = config['projects']

    # convert short ID to long ID
    if len(project_id) == 12:
        for p_id in projects:
            if p_id[-12:] == project_id:
                project_id = p_id
                break
    
    if project_id not in projects:
        msg = 'Project with id {} does not exists'.format(project_id)
        print(msg, file=sys.stderr)
        sys.exit(1)

    # generate random ID
    m = hashlib.sha1()
    m.update('{}'.format(random.randint(0, 2 ** 128)).encode())
    container_id = m.hexdigest()

    container = {
        'id': container_id,
        'project_id': project_id,
        'address': remote_address,
        'name': name,
        'ports': ports,
        'distro': distro,
        'image_id': image_id,
        'image': image,
    }

    containers[container_id] = container
    save_consensus_config(config)
    print('{}'.format(container_id))


def container_remove(remote_uri, project_id, container_id):
    remote_username, remote_address = remote_uri.split('@')
    config = load_consensus_config(remote_uri)
    containers = config['containers']

    # check if project id exists
    projects = config['projects']

    # convert short ID to long ID
    if len(project_id) == 12:
        for p_id in projects:
            if p_id[-12:] == project_id:
                project_id = p_id
                break

    if project_id not in projects:
        msg = 'Project with id {} does not exists'.format(project_id)
        print(msg, file=sys.stderr)
        sys.exit(1)

    # convert short ID to long ID
    if len(container_id) == 12:
        for c_id in containers:
            if c_id[-12:] == container_id:
                container_id = c_id
                break

    if container_id not in containers:
        msg = 'Container with id {} does not exists'.format(container_id)
        print(msg, file=sys.stderr)
        sys.exit(1)

    del containers[container_id]
    save_consensus_config(config)
    print('{}'.format(container_id))


def container_start(remote_uri, project_id, container_id):
    pass


def container_stop(remote_uri, project_id, container_id):
    pass


def container_restart(remote_uri, project_id, container_id):
    pass


def container_migrate(remote_uri, project_id, container_id):
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='systemd-nspawn deployment')
    parser_subparsers = parser.add_subparsers(dest='subparser', metavar='main')
    parser.add_argument('--remote-address', '-r', help='Remote address')
    # parser.add_argument('--project-id', '-C', help='Project ID')
    
    # machine
    machine_parser = parser_subparsers.add_parser('machine')
    machine_subparsers = machine_parser.add_subparsers(dest='machine_subparser', metavar='machine')
    
    # machine list
    machine_list_parser = machine_subparsers.add_parser('list', help='List machines')

    # machine add
    machine_add_parser = machine_subparsers.add_parser('add', help='Add machine')
    machine_add_parser.add_argument('--id', '-I', help='Machine ID')
    machine_add_parser.add_argument('--address', '-a', help='[USER="root"@]HOST[:PORT=22]')

    # machine remove
    machine_remove_parser = machine_subparsers.add_parser('remove', help='Remove machine')
    machine_remove_parser.add_argument('--id', '-I', help='Machine ID')
    
    # project
    project_parser = parser_subparsers.add_parser('project')
    project_subparsers = project_parser.add_subparsers(dest='project_subparser', metavar='project')

    # project list
    project_list_parser = project_subparsers.add_parser('list', help='List projects')

    # project add
    project_add_parser = project_subparsers.add_parser('add', help='Add project')
    project_add_parser.add_argument('--id', '-I', default=None, help='Project ID')
    project_add_parser.add_argument('--name', '-n', help='Name')

    # project remove
    project_remove_parser = project_subparsers.add_parser('project', help='Remove project')
    project_remove_parser.add_argument('--id', '-I', help='Project ID')

    # container 
    container_parser = parser_subparsers.add_parser('container')
    container_subparsers = container_parser.add_subparsers(dest='container_subparser', metavar='container')
    container_parser.add_argument('--project-id', '-P', help='Project ID')
    
    # container list
    container_list_parser = container_subparsers.add_parser('list', help='List of containers at remote host')

    # container add
    container_add_parser = container_subparsers.add_parser('add', help='Add container')
    container_add_parser.add_argument('--address', '-a', default=None, help='[USER="root"@]HOST[:PORT=22]')
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
    # print(args)

    if args.subparser == 'machine':
        if args.machine_subparser == 'list':
            machine_list(args.remote_address)
        elif args.machine_subparser == 'add':
            machine_add(args.remote_address, args.address)
        elif args.machine_subparser == 'remove':
            machine_remove(args.remote_address, args.id)
    elif args.subparser == 'project':
        if args.project_subparser == 'list':
            project_list(args.remote_address)
        elif args.project_subparser == 'add':
            project_add(args.remote_address, args.name)
        elif args.project_subparser == 'remove':
            project_remove(args.remote_address, args.id)
    elif args.subparser == 'container':
        if args.container_subparser == 'list':
            container_list(args.remote_address, args.project_id)
        elif args.container_subparser == 'add':
            container_add(args.remote_address, args.project_id, args.address, args.name, args.ports, args.distro, args.image_id, args.image)
        elif args.container_subparser == 'remove':
            container_remove(args.remote_address, args.project_id, args.id)
        elif args.container_subparser == 'start':
            container_start(args.remote_address, args.project_id, args.id)
        elif args.container_subparser == 'stop':
            container_stop(args.remote_address, args.project_id, args.id)
        elif args.container_subparser == 'restart':
            container_restart(args.remote_address, args.project_id, args.id)
        elif args.container_subparser == 'migrate':
            container_migrate(args.remote_address, args.project_id, args.id)
