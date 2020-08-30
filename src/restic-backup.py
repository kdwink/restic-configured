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
# LIST FILES    : ./restic-backup.py config/example.json ls <snapshot|latest>
# CHECK         : ./restic-backup.py config/example.json check
# STATS         : ./restic-backup.py config/example.json stats
# PRUNE         : ./restic-backup.py config/example.json prune
# RESTORE       : ./restic-backup.py config/example.json restore <snapshot|latest> /etc /tmp/restored/etc
# UNLOCK        : ./restic-backup.py config/example.json unlock
#
# DOCS:
#
# https://restic.readthedocs.io/en/latest/
# ==============================================================================
import argparse
import datetime
import os
import subprocess
import sys
import time
import config as conf


# --------------------------------------------------------------------
# general purpose functions
#
# --------------------------------------------------------------------


def redirect_stdout(config):
    timestamp = datetime.datetime.now().replace(microsecond=0).isoformat('_')
    log_dir = config.log_directory
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)
    script_dir = os.path.dirname(os.path.realpath(__file__))
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

def execute_restic(config, args, additional_args):
    password_command = f"{sys.argv[0]} {args.config_file} password"
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


def command_check(config, args): execute_restic(config, args, ['check'])


def command_stats(config, args):  execute_restic(config, args, ['stats', '--mode', 'raw-data'])


def command_prune(config, args): execute_restic(config, args, ['prune'])


def command_forget(config, args):
    for backup_path in config.backup_paths:
        policy = config.forget_policy if not backup_path.has_forgets() else backup_path.forget_policy
        execute_restic(config, args, ['forget', '--path', backup_path.path] + policy)


def command_ls(config, args):
    command = args.sub_command
    if len(command) != 2:
        print(f"usage: {command[0]} [snapshot|'latest']")
        exit(-1)
    execute_restic(config, args, ['ls', '--long', command[1]])


def command_restore(config, args):
    command = args.sub_command
    if len(command) != 4:
        print(f"usage: {command[0]} [snapshot|'latest'] [restore-path] [extract-to-path]")
        exit(-1)
    execute_restic(config, args, ['restore', command[1], '--path', command[2], '--target', command[3]])


def command_backup(config, args):
    for backup_path in config.backup_paths:
        banner(f"backing up '{backup_path.path}'")
        a = ["backup", "--one-file-system", backup_path.path]
        if backup_path.has_excludes():
            for e in backup_path.excludes:
                a = a + ['--exclude', e.pattern]
        execute_restic(config, args, a)


def command_snapshots(config, args): execute_restic(config, args, ['snapshots'])


def command_unlock(config, args): execute_restic(config, args, ['unlock'])


def command_init(config, args): execute_restic(config, args, ['init'])


def command_password(config, args):
    print(config.password, end='')
    exit(0)


# --------------------------------------------------------------------
#
# main
#
# --------------------------------------------------------------------


def main():
    start_time = time.perf_counter()

    parser = argparse.ArgumentParser(description='Restic backup tool.', add_help=True, allow_abbrev=False)
    parser.add_argument("config_file", help="Configuration file.")
    parser.add_argument("sub_command", help="Sub command.", nargs='*')
    parser.add_argument('-l', '--log', action='store_true')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 2.0')
    args = parser.parse_args()

    valid_commands = {
        'backup': command_backup,
        'check': command_check,
        'forget': command_forget,
        'init': command_init,
        'ls': command_ls,
        'password': command_password,
        'prune': command_prune,
        'restore': command_restore,
        'stats': command_stats,
        'snapshots': command_snapshots,
        'unlock': command_unlock,
    }

    if len(args.sub_command) < 1:
        print(f"missing sub-command: {list(valid_commands.keys())}")
        sys.exit(-1)

    if args.sub_command[0] not in valid_commands:
        print(f"BAD sub-command: '{args.sub_command[0]}'")
        sys.exit(-1)

    config = conf.read_config(args.config_file)

    if args.log:
        redirect_stdout(config)

    if args.sub_command[0] != 'password':
        banner("config")
        conf.print_config(config)
        banner("starting")

    valid_commands[args.sub_command[0]](config, args)

    banner(f"COMPLETE in {time.perf_counter() - start_time:,.0f} seconds.")


main()
