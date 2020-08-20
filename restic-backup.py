#!/usr/bin/env python3
# ==============================================================================
#
# ==============================================================================
import json
import sys
import subprocess

if len(sys.argv) != 3:
    print(f'usage: {sys.argv[0]} <config-file> <command>')
    exit(-1)


def print_config(config):
    print("------------------------------------------------------")
    print(f"repository = {config['repository']}")
    for path in config['backup-paths']:
        print(f"path = {path['path']}")
    for exclude in config['exclude-patterns']:
        print(f"exclude = {exclude['pattern']}")
    print("------------------------------------------------------")


def read_config(file):
    with open(file, 'rb') as f:
        read_bytes = f.read()
        json_string = read_bytes.decode('utf-8')
        return json.loads(json_string)


def execute_restic(config, additional_args):
    password_command = f"{sys.argv[0]} {sys.argv[1]} password"
    c = [
            "restic",
            "--verbose",
            "--password-command", password_command,
            "--repo", config['repository']
        ] + additional_args
    print(f'command: {c}')
    result = subprocess.run(c, capture_output=False)
    # restic --password-file "${P}" --repo "${R}" init;


def main(config_file_path, command):
    config = read_config(config_file_path)
    if command != 'password':
        print(f'configuration file path = {config_file_path}')
        print_config(config)

    if command == 'init':
        execute_restic(config, ['init'])
    elif command == 'backup':
        for backup_path in config['backup-paths']:
            execute_restic(config, ["backup", "--one-file-system", backup_path['path']])
    elif command == 'password':
        print(config['password'])


main(sys.argv[1], sys.argv[2])
