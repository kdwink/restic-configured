#!/usr/bin/env python3
# ==============================================================================
#
# ==============================================================================
import json
import sys
import subprocess
import datetime

if len(sys.argv) != 3:
    print(f'usage: {sys.argv[0]} <config-file> <command>')
    exit(-1)


def banner(message):
    timestamp = datetime.datetime.now().replace(microsecond=0).isoformat(' ')
    print(f'{timestamp} ##################### {message}')


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
    subprocess.run(args, capture_output=False)


def main(config_file_path, command):
    config = read_config(config_file_path)
    if command != 'password':
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
        print(config['password'])
        exit(0)
    else:
        print(f"BAD COMMAND: {command}")
        exit(0)


main(sys.argv[1], sys.argv[2])
banner("complete")
