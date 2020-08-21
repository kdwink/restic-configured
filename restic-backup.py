#!/usr/bin/env python3
# ==============================================================================
#
# ==============================================================================
import datetime
import json
import os
import subprocess
import sys
import time

script_dir = os.path.dirname(os.path.realpath(__file__))

if len(sys.argv) < 3 or len(sys.argv) > 6:
    print(f'usage: {sys.argv[0]} <config-file> <command>')
    exit(-1)


def redirect_stdout(config):
    timestamp = datetime.datetime.now().replace(microsecond=0).isoformat('_')
    log_dir = config['log-directory']
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)
    log_file = f"{script_dir}/{log_dir}/{timestamp}.log"
    sys.stdout = open(log_file, 'w')


def banner(message):
    timestamp = datetime.datetime.now().replace(microsecond=0).isoformat('_')
    print(f'[{timestamp}] *************** {message}')
    sys.stdout.flush()


def print_config(config):
    banner("configuration")
    print(f"repository    = {config['repository']}")
    print(f"log-directory = {config['log-directory']}")
    for backup_path in config['backup-paths']:
        print(f"\tpath = {backup_path['path']}")
        if 'excludes' in backup_path:
            for exclude in backup_path['excludes']:
                print(f"\t\texclude = {exclude['pattern']}")
    env = config.get('environment')
    if env is not None:
        print("\tenvironment:")
        for key, value in env.items():
            print(f"\t\t{key} = {value}")


def read_config(file):
    f = file if os.path.isabs(file) else f"{script_dir}/{file}"
    with open(f, 'rb') as f:
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
    banner(f"command\n\n{' '.join(args)}\n")
    t = subprocess.run(args,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT,
                       text=True,
                       env=config.get('environment')
                       )
    print(t.stdout)


def main(config_file_path, command):
    start_time = time.perf_counter()
    config = read_config(config_file_path)

    if command == 'password':
        print(config['password'], end='')
        exit(0)

    redirect_commands = ['backup', 'prune']

    if command in redirect_commands:
        redirect_stdout(config)

    print_config(config)

    banner("starting")

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

    elif command == 'prune':
        banner("forget")
        execute_restic(config, ['forget', '--keep-daily', '7', '--keep-weekly', '5', '--keep-monthly', '12'])
        banner("prune")
        execute_restic(config, ['--cleanup-cache', 'prune'])
        banner("check")
        execute_restic(config, ['check'])
        banner("stats")
        execute_restic(config, ['stats', '--mode', 'raw-data'])

    else:
        print(f"BAD COMMAND: {command}")
        exit(0)

    banner(f"COMPLETE in {time.perf_counter() - start_time:,.0f} seconds.")


main(sys.argv[1], sys.argv[2])
