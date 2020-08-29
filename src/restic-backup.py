#!/usr/bin/env python3
# ==============================================================================
# Restic backup script.
#
# SETUP:
#
# apt-get install restic
# brew install restic
#
# USAGE:
#
# INIT          : ./restic-backup.py config/example.json init
# LIST SNAPSHOTS: ./restic-backup.py config/example.json snapshots
# BACKUP        : ./restic-backup.py config/example.json backup
# LIST FILES    : ./restic-backup.py config/example.json ls latest
# CHECK         : ./restic-backup.py config/example.json check
# STATS         : ./restic-backup.py config/example.json stats
# PRUNE         : ./restic-backup.py config/example.json prune
# RESTORE       : ./restic-backup.py config/example.json restore latest /etc /tmp/restored/etc
# UNLOCK        : ./restic-backup.py config/example.json unlock
#
# DOCS:
#
# https://restic.readthedocs.io/en/latest/
# ==============================================================================
import datetime
import os
import subprocess
import sys
import time
import config as conf

script_dir = os.path.dirname(os.path.realpath(__file__))

# --------------------------------------------------------------------
#
# general purpose functions
#
# --------------------------------------------------------------------


if len(sys.argv) < 3 or len(sys.argv) > 6:
    print(f'usage: {sys.argv[0]} <config-file> <command>')
    exit(-1)


def redirect_stdout(config):
    timestamp = datetime.datetime.now().replace(microsecond=0).isoformat('_')
    log_dir = config.log_directory
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)
    log_file = f"{script_dir}/{log_dir}/{timestamp}.log"
    sys.stdout = open(log_file, 'w')


def banner(message):
    timestamp = datetime.datetime.now().replace(microsecond=0).isoformat('_')
    print(f'[{timestamp}] *************** {message}')
    sys.stdout.flush()


def format_command(command_part_array):
    result = ""
    length = 0
    last_part = ""
    for part in command_part_array:
        new_len = length + len(part)
        new_line = (part.startswith("--") and (new_len > 40)) or (new_len > 80)
        if new_line:
            length = 0
            result = result + "\\\n\t"
        should_quote_part = (' ' in part or last_part == '--exclude')
        result = result + (part if not should_quote_part else f'"{part}"')
        result = result + " "
        length = length + len(part)
        last_part = part
    return result


# --------------------------------------------------------------------
#
# command execution
#
# --------------------------------------------------------------------

def execute_restic(config, additional_args):
    password_command = f"{sys.argv[0]} {sys.argv[1]} password"
    args = [
               "restic",
               "--repo", config.repository,
               "--verbose",
               "--password-command", password_command
           ] + additional_args
    banner(f"command\n\n{format_command(args)}\n")
    t = subprocess.run(args,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT,
                       text=True,
                       env=config.environment
                       )
    print(t.stdout)


def command_check(config): execute_restic(config, ['check'])


def command_stats(config):  execute_restic(config, ['stats', '--mode', 'raw-data'])


def command_prune(config):
    execute_restic(config, ['prune'])


def command_forget(config):
    for backup_path in config.backup_paths:
        policy = config.forget_policy if not backup_path.has_forgets() else backup_path.forget_policy
        execute_restic(config, ['forget', '--path', backup_path.path] + policy)


def command_ls(config):
    if len(sys.argv) != 4:
        print(f"usage: {sys.argv[0]} [config-file] ls [snapshot|'latest']")
        exit(-1)
    execute_restic(config, ['ls', '--long', sys.argv[3]])


def command_restore(config):
    if len(sys.argv) != 6:
        print(f"usage: {sys.argv[0]} [config-file] restore [snapshot|'latest'] [restore-path] [extract-to-path]")
        exit(-1)
    execute_restic(config, ['restore', sys.argv[3], '--path', sys.argv[4], '--target', sys.argv[5]])


def command_backup(config):
    for backup_path in config.backup_paths:
        banner(f"backing up '{backup_path.path}'")
        a = ["backup", "--one-file-system", backup_path.path]
        if backup_path.has_excludes():
            for e in backup_path.excludes:
                a = a + ['--exclude', e.pattern]
        execute_restic(config, a)


def command_snapshots(config):
    execute_restic(config, ['snapshots'])


def command_unlock(config):
    execute_restic(config, ['unlock'])


def command_init(config):
    execute_restic(config, ['init'])


# --------------------------------------------------------------------
#
# main
#
# --------------------------------------------------------------------


def main(config_file_path, command):
    start_time = time.perf_counter()
    config = conf.read_config(config_file_path)

    if command == 'password':
        print(config.password, end='')
        exit(0)

    redirect_commands = ['backup', 'prune']

    if command in redirect_commands:
        redirect_stdout(config)

    conf.print_config(config)

    banner("starting")

    if command == 'init':
        command_init(config)
    elif command == 'unlock':
        command_unlock(config)
    elif command == 'forget':
        command_forget(config)
    elif command == 'snapshots':
        command_snapshots(config)
    elif command == 'check':
        command_check(config)
    elif command == 'stats':
        command_stats(config)
    elif command == 'ls':
        command_ls(config)
    elif command == 'restore':
        command_restore(config)
    elif command == 'backup':
        command_backup(config)
    elif command == 'prune':
        command_prune(config)
    else:
        print(f"BAD COMMAND: {command}")
        exit(0)

    banner(f"COMPLETE in {time.perf_counter() - start_time:,.0f} seconds.")


main(sys.argv[1], sys.argv[2])
