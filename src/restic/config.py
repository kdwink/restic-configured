def _check_props(d, props):
    for prop in d.keys():
        if prop not in props:
            raise ValueError(f"invalid property: `{prop}`")


class Configuration:
    __valid_props = ["backup-paths", "description", "forget-policy",
                     "log-directory", "password", "repository"]

    def __init__(self, d):
        _check_props(d, self.__valid_props)
        self.repository = d['repository']
        self.password = d['password']
        self.log_directory = d['log-directory']
        # optional at this level
        self.forget_policy = d.get('forget-policy')
        self.backup_paths = list(map(lambda x: BackupPath(x), d['backup-paths']))


class BackupPath:
    __valid_props = ["description", "excludes", "forget-policy", "path"]

    def __init__(self, d):
        _check_props(d, self.__valid_props)
        self.path = d['path']
        self.forget_policy = d.get('forget-policy')
        if 'excludes' in d:
            self.excludes = list(map(lambda x: Exclude(x), d.get('excludes')))
        else:
            self.excludes = None


class Exclude:
    __valid_props = ["description", "pattern"]

    def __init__(self, d):
        if isinstance(d, str):
            self.pattern = d
            self.description = None
        elif isinstance(d, dict):
            _check_props(d, self.__valid_props)
            self.pattern = d['pattern']
            self.description = d.get('description')
        else:
            pass
