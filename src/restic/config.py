import json
import os
import sys


# --------------------------------------------------------------------
#
# classes
#
# --------------------------------------------------------------------


class Configuration:
    __valid_props = ["backup-paths", "backup-commands", "environment",
                     "forget-policy", "log-directory", "log-retention-days",
                     "note", "password", "prune-policy", "repository",
                     "restic-path"]

    def __init__(self, d, src_dir):
        self.src_dir = src_dir
        # check
        _check_props(d, self.__valid_props)
        # repository
        self.repository = d['repository'].strip()
        check(len(self.repository) > 0, "value for 'repository' cannot be empty")
        # environment
        self.environment = d.get('environment')
        check(self.environment is None or isinstance(self.environment, dict), "environment must have keys and values")
        # password
        self.password = d['password'].strip()
        check(len(self.password) > 0, "value for 'password' cannot be empty")
        # log directory
        self.log_directory = d['log-directory'].strip()
        check(len(self.log_directory) > 0, "value for 'log-directory' cannot be empty")
        # log-retention-days
        self.log_retention_days = d.get('log-retention-days', 365 * 2)
        # forget-policy: optional at this level
        self.forget_policy = d.get('forget-policy')
        if self.forget_policy is not None and len(self.forget_policy) == 0:
            self.forget_policy = None
        # prune-policy
        self.prune_policy = d.get('prune-policy', 0)
        check(0 <= self.prune_policy <= 1, "prune-policy must be [0,1] probability of running prune")
        # backup commands
        self.backup_commands = []
        if 'backup-commands' in d:
            commands_ = d['backup-commands']
            self.backup_commands = list(map(lambda x: BackupCommand(x), commands_))
        # backup paths
        self.backup_paths = []
        if 'backup-paths' in d:
            paths_ = d['backup-paths']
            self.backup_paths = list(map(lambda x: BackupPath(x), paths_))
            _check_for_duplicates(list(map(lambda x: x.path, self.backup_paths)), "duplicate path value")
        check(len(self.backup_paths) + len(self.backup_commands) > 0, "no backup paths or commands defined")
        # restic-path
        self.restic_path = d.get('restic-path', 'restic')
        check(isinstance(self.restic_path, str), "expected restic-path to be a string")
        check(len(self.restic_path.strip()) > 0, "expected a non-empty value for restic-path")

    def has_environment(self):
        return self.environment is not None

    def restic_path_abs(self):
        return self._abs_path(self.restic_path)

    def log_directory_abs(self):
        return self._abs_path(self.log_directory)

    def _abs_path(self, path):
        return path if os.path.isabs(path) else os.path.normpath(f"{self.src_dir}/{path}")


class BackupPath:
    __valid_props = ["excludes", "forget-policy", "note", "path"]

    def __init__(self, d):
        _check_props(d, self.__valid_props)
        self.path = d['path']
        self.forget_policy = d.get('forget-policy')
        if self.forget_policy is not None and len(self.forget_policy) == 0:
            self.forget_policy = None
        if 'excludes' in d:
            self.excludes = list(map(lambda x: Exclude(x), d.get('excludes')))
            _check_for_duplicates(list(map(lambda x: x.pattern, self.excludes)), "duplicate exclude path")
        else:
            self.excludes = None

    def has_excludes(self):
        return self.excludes is not None

    def has_forgets(self):
        return self.forget_policy is not None


class BackupCommand:
    __valid_props = ["command", "note", "repo-path"]

    def __init__(self, d):
        _check_props(d, self.__valid_props)
        self.command = d['command']
        self.repo_path = d['repo-path']
        check(isinstance(self.command, list), "expected command to be a list")
        check(isinstance(self.repo_path, str), "expected repo-path to be a string")
        check(len(self.command) > 0, "expected command list to have at least one element")
        # restic add as slash if you don't and then commands like forget don't work
        # if you don't use a leading slash.
        check(self.repo_path.startswith("/"), "repo path for commands must start with forward slash")


class Exclude:
    __valid_props = ["note", "pattern"]

    def __init__(self, d):
        if isinstance(d, str):
            self.pattern = d.strip()
            self.note = None
        elif isinstance(d, dict):
            _check_props(d, self.__valid_props)
            self.pattern = d['pattern'].strip()
            self.note = d.get('note')
        else:
            raise ValueError("unexpected type for exclude element: " + str(type(d)))
        check(len(self.pattern) > 0, "exclude pattern can not be empty")


# --------------------------------------------------------------------
#
# functions
#
# --------------------------------------------------------------------

def print_env():
    python_ver = sys.version.replace("\n", " ")
    print(f"sys.version        = {python_ver}")
    print(f"USER               = {os.environ.get('USER')}")
    print(f"HOME               = {os.environ.get('HOME')}")


def print_config(config: Configuration):
    print(f"repository         = {config.repository}")
    print(f"restic-path        = {config.restic_path}")
    print(f"log-directory      = {config.log_directory}")
    print(f"log-retention-days = {config.log_retention_days}")
    print(f"forget-policy      = {config.forget_policy}")
    print(f"prune-policy       = {config.prune_policy}")
    for backup_command in config.backup_commands:
        print(f"\t{backup_command.command} > {backup_command.repo_path}")
    for backup_path in config.backup_paths:
        print(f"\tpath = {backup_path.path}")
        if backup_path.has_forgets():
            print(f"\t\tforget-policy={backup_path.forget_policy}")
        if backup_path.has_excludes():
            for e in backup_path.excludes:
                print(f"\t\texclude = {e.pattern}")
    if config.has_environment():
        print("\tenvironment:")
        for key, value in config.environment.items():
            print(f"\t\t{key} = {value}")


def read_config(file, src_dir):
    json_string = _read_config_json(file, src_dir)
    return Configuration(json_string, src_dir)


def check(condition, message):
    if not condition: raise ValueError(message)


# --------------------------------------------------------------------
#
# private functions
#
# --------------------------------------------------------------------

def _read_config_json(file, relative_dir):
    f = file if os.path.isabs(file) else f"{relative_dir}/{file}"
    if not os.path.isfile(f):
        print("specified configuration files does not exist:" + f)
        sys.exit(-1)
    with open(f, 'rb') as f:
        read_bytes = f.read()
        json_string = read_bytes.decode('utf-8')
        return json.loads(json_string)


def _check_props(d, props):
    for prop in d.keys():
        if prop not in props:
            raise ValueError(f"invalid property: '{prop}'")


def _check_for_duplicates(in_list, message):
    for element in in_list:
        if in_list.count(element) > 1:
            raise ValueError(f"{message}: '{element}'")
