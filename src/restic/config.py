def _check_props(d, props):
    for prop in d.keys():
        if prop not in props:
            raise ValueError(f"invalid property: '{prop}'")


def _check_for_duplicates(in_list, message):
    for element in in_list:
        if in_list.count(element) > 1:
            raise ValueError(f"{message}: '{element}'")


class Configuration:
    __valid_props = ["backup-paths", "description", "forget-policy",
                     "log-directory", "password", "repository"]

    def __init__(self, d):
        _check_props(d, self.__valid_props)
        # repository
        self.repository = d['repository'].strip()
        if len(self.repository) == 0:
            raise ValueError("value for 'repository' cannot be empty")
        # password
        self.password = d['password'].strip()
        if len(self.password) == 0:
            raise ValueError("value for 'password' cannot be empty")
        # log directory
        self.log_directory = d['log-directory'].strip()
        if len(self.log_directory) == 0:
            raise ValueError("value for 'log-directory' cannot be empty")
        # forget-policy: optional at this level
        self.forget_policy = d.get('forget-policy')
        if self.forget_policy is not None and len(self.forget_policy) == 0:
            self.forget_policy = None
        # backup paths
        paths_ = d['backup-paths']
        if len(paths_) < 1: raise ValueError("no backup paths defined")
        self.backup_paths = list(map(lambda x: BackupPath(x), paths_))
        _check_for_duplicates(list(map(lambda x: x.path, self.backup_paths)), "duplicate path value")


class BackupPath:
    __valid_props = ["description", "excludes", "forget-policy", "path"]

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


class Exclude:
    __valid_props = ["description", "pattern"]

    def __init__(self, d):
        if isinstance(d, str):
            self.pattern = d.strip()
            self.description = None
        elif isinstance(d, dict):
            _check_props(d, self.__valid_props)
            self.pattern = d['pattern'].strip()
            self.description = d.get('description')
        else:
            raise ValueError("unexpected type for exclude element: " + str(type(d)))
        if len(self.pattern) == 0:
            raise ValueError("exclude pattern can not be empty")
