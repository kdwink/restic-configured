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
# INIT          : ./backup.py config/example.json init
# LIST SNAPSHOTS: ./backup.py config/example.json snapshots
# BACKUP        : ./backup.py config/example.json backup
# LIST FILES    : ./backup.py config/example.json ls <snapshot|latest>
# CHECK         : ./backup.py config/example.json check
# STATS         : ./backup.py config/example.json stats
# PRUNE         : ./backup.py config/example.json prune
# RESTORE       : ./backup.py config/example.json restore <snapshot|latest> /etc /tmp/restored/etc
# UNLOCK        : ./backup.py config/example.json unlock
#
# DOCS:
#
# https://restic.readthedocs.io/en/latest/
# ==============================================================================
import argparse
import os
import random
import subprocess
import sys
import time
from restic.config import read_config, print_config, print_env
from restic.logging import banner, redirect_stdout, format_command
from restic.version import read_version


# --------------------------------------------------------------------
#
# command execution
#
# --------------------------------------------------------------------


def execute_restic(config, args, additional_args, stdin=None):
    password_command = f"{sys.argv[0]} {args.config_file} password"
    subprocess_args = [
                          config.restic_path_abs(),
                          "--repo", config.repository,
                          "--password-command", password_command
                      ] + additional_args
    banner(f"{additional_args[0]}\n\n{format_command(subprocess_args)}\n")
    t = subprocess.run(subprocess_args,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT,
                       text=True,
                       env=config.environment,
                       stdin=stdin
                       )
    print(t.stdout)


def command_check(config, args): execute_restic(config, args, ['check'])


def command_stats(config, args):  execute_restic(config, args, ['stats', '--mode', 'raw-data'])


def command_prune(config, args): execute_restic(config, args, ['prune'])


def command_forget(config, args):
    for backup_command in config.backup_commands:
        execute_restic(config, args, ['forget', '--path', backup_command.repo_path] + config.forget_policy)
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
    for bc in config.backup_commands:
        banner(f"backing up COMMAND result '{bc.command}'")
        with subprocess.Popen(bc.command, stdout=subprocess.PIPE) as ps:
            a = ["backup", "--stdin", "--stdin-filename", bc.repo_path]
            execute_restic(config, args, a, ps.stdout)
            ps.wait()

    for bp in config.backup_paths:
        banner(f"backing up PATH '{bp.path}'")
        a = ["backup", "--one-file-system", bp.path]
        if bp.has_excludes():
            for e in bp.excludes:
                a = a + ['--exclude', e.pattern]
        execute_restic(config, args, a)


def command_snapshots(config, args): execute_restic(config, args, ['snapshots'])


def command_unlock(config, args): execute_restic(config, args, ['unlock'])


def command_init(config, args): execute_restic(config, args, ['init'])


# noinspection PyUnusedLocal
def command_password(config, args):
    print(config.password, end='')
    exit(0)


def command_backup_prune(config, args):
    command_backup(config, args)
    p_random = random.random()
    if config.prune_policy != 0 and p_random <= config.prune_policy:
        command_forget(config, args)
        command_prune(config, args)
        command_check(config, args)
    command_stats(config, args)


# --------------------------------------------------------------------
#
# main
#
# --------------------------------------------------------------------


def main():
    start_time = time.perf_counter()

    version_string = read_version()

    parser = argparse.ArgumentParser(description='Restic backup tool.', add_help=True, allow_abbrev=False)
    parser.add_argument("config_file", help="Configuration file.")
    parser.add_argument("sub_command", help="Sub command.", nargs='*')
    parser.add_argument('-l', '--log', action='store_true')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {version_string}')
    args = parser.parse_args()

    valid_commands = {
        'backup': command_backup,
        'backup-prune': command_backup_prune,
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

    src_dir = os.path.dirname(os.path.abspath(__file__))
    config = read_config(args.config_file, src_dir)

    if args.log:
        redirect_stdout(config)

    if args.sub_command[0] != 'password':
        banner("env")
        print_env()
        banner("config")
        print_config(config)
        banner("starting")

    valid_commands[args.sub_command[0]](config, args)

    banner(f"COMPLETE in {time.perf_counter() - start_time:,.0f} seconds.")


main()
