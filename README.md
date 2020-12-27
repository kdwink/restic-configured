# restic-backup

A python script that invokes restic ( https://github.com/restic/restic ).


# Features

- [ ] Ability to execute arbitrary command for other repos.
- [x] Package restic executable with script deployable.
- [x] Allow restic path to be configured.
- [x] Packing for easy installation/upgrade on remote hosts.
- [x] Give a better error message if configuration file does not exist.
- [x] Auto cleanup/rotation of logs.
- [x] Single execution from cron (does both backup and forget and/or prune)
- [x] Make redirect of output optional command line arg.
- [x] Validate config file. Assert required fields and error on unrecognized fields.
- [x] Singe configuration file for: password, excludes, and backup dirs
- [x] Forget settings are configurable per project in configuration json.
- [x] Ability to more easily execute arbitrary restic commands.


# Installation

Extracted contents of tar file will have this structure:
```text
    restic-backup/
        config/
        bin/
        src/
            backup.py
```

Create a cron script that invokes backup.py like so:
```shell
19 18 * * * /root/restic/src/backup.py --log ../config/dev.json backup-prune
```


## OSX setup

On OSX it may be necessary to grant `/usr/sbin/cron` "Full Disk Access" permission.  Settings -> 
Security & Privacy -> Full Disk Access.



# Configuration

Relative paths in the configuration file are interpreted as relative to the location
of the primary script, `backup.py`.


# Notes

## Restic forget vs prune

Forget and prune are separate commands to allow the use case where several machines might all sync to the same
repository and only issue forget commands, possibly each with a unique policy, while a single machine, possibly
close to the repository, issues the prune command.

## Pattern matching:

* https://restic.readthedocs.io/en/latest/040_backup.html#excluding-files
* Pattern is matched against entire file path.
* Trailing / in a pattern is ignored, leading / anchors pattern to root directory.
* Pattern must match one or more complete file/directory components of path.
* Single * wildcard does NOT match over directory separator
