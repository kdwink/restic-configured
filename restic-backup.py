#!/usr/bin/env python3
# ==============================================================================
#
# ==============================================================================
import json
import sys

if len(sys.argv) != 3:
    print(f'usage: {sys.argv[0]} <config-file> <command>')
    exit(-1)


def print_config(config):
    print(f"repository = {config['repository']}")
    for path in config['backup-paths']:
        print(f"path = {path['path']}")
    for exclude in config['exclude-patterns']:
        print(f"exclude = {exclude['pattern']}")


def read_config(file):
    with open(file, 'rb') as f:
        read_bytes = f.read()
        json_string = read_bytes.decode('utf-8')
        return json.loads(json_string)


def main(config_file_path):
    print(f'configuration file path = {config_file_path}')
    config = read_config(config_file_path)
    print_config(config)


main(sys.argv[1])
