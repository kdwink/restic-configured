#!/usr/bin/env python3
# ==============================================================================
#
# ==============================================================================
import datetime
import json
import os
import subprocess
import sys

if len(sys.argv) < 3 or len(sys.argv) > 6:
    print(f'usage: {sys.argv[0]} <config-file> <command>')
    exit(-1)


def redirect_stdout(config):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    timestamp = datetime.datetime.now().replace(microsecond=0).isoformat('_')
    log_dir = config['log-directory']
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)
    log_file = f"{script_dir}/{log_dir}/{timestamp}.log"
    sys.stdout = open(log_file, 'w')


def banner(message):
    timestamp = datetime.datetime.now().replace(microsecond=0).isoformat(' ')
    print(f'{timestamp} ############# {message}')


def print_config(config):
    print("------------------------------------------------------")
    print(f"repository = {config['repository']}")
    for backup_path in config['backup-paths']:
        print(f"path = {backup_path['path']}")
        if 'excludes' in backup_path:
            for exclude in backup_path['excludes']:
                print(f"\texclude = {exclude['pattern']}")
    print("------------------------------------------------------")


def read_config(file):
    with open(file, 'rb') as f:
        read_bytes = f.read()
        json_string = read_bytes.decode('utf-8')
        return json.loads(json_string)


def execute_restic(config, additional_args):
    password_command = f"{sys.argv[0]} {sys.argv[1]} password"
    args = [
               "restic",
               "--verbose",
               "--password-command", password_command,
               "--repo", config['repository']
           ] + additional_args
    print(f'command: {" ".join(args)}')
    t = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(t.stdout)

def main(config_file_path, command):

    config = read_config(config_file_path)

    if command != 'password':
        redirect_stdout(config)
        banner("starting")
        print(f'configuration file path = {config_file_path}')
        print_config(config)

    if command == 'init':
        execute_restic(config, ['init'])

    elif command == 'unlock':
        execute_restic(config, ['unlock'])

    elif command == 'snapshots':
        execute_restic(config, ['snapshots'])

    elif command == 'check':
        execute_restic(config, ['check'])

    elif command == 'stats':
        execute_restic(config, ['stats', '--mode', 'raw-data'])

    elif command == 'ls':
        if len(sys.argv) != 4:
            print(f"usage: {sys.argv[0]} [config-file] ls [snapshot|'latest']")
            exit(-1)
        execute_restic(config, ['ls', '--long', sys.argv[3]])

    elif command == 'restore':
        if len(sys.argv) != 6:
            print(f"usage: {sys.argv[0]} [config-file] restore [snapshot|'latest'] [restore-path] [extract-to-path]")
            exit(-1)
        execute_restic(config, ['restore', sys.argv[3], '--path', sys.argv[4], '--target', sys.argv[5]])

    elif command == 'backup':
        for backup_path in config['backup-paths']:
            current_path = backup_path['path']
            banner(f"backing up '{current_path}'")
            a = ["backup", "--one-file-system", current_path]
            if 'excludes' in backup_path:
                for exclude in backup_path['excludes']:
                    a = a + ['--exclude', exclude['pattern']]
            execute_restic(config, a)

    elif command == 'password':
        print(config['password'], end='')
        exit(0)

    else:
        print(f"BAD COMMAND: {command}")
        exit(0)

    banner("complete")

main(sys.argv[1], sys.argv[2])
