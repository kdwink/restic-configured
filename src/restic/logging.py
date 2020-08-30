import datetime
import os
import sys


def timestamp(): return datetime.datetime.now().replace(microsecond=0).isoformat('_')


def redirect_stdout(config, relative_dir):
    log_dir = config.log_directory
    d = log_dir if os.path.isabs(log_dir) else f"{relative_dir}/{log_dir}"
    if not os.path.isdir(d):
        os.makedirs(d)
    sys.stdout = open(f"{d}/{timestamp()}.log", 'w')


def banner(message):
    print(f'[{timestamp()}] *************** {message}')
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

