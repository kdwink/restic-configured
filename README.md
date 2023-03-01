# restic-configured

A python script that invokes [restic](https://github.com/restic/restic) with options (backup paths, exclude paths,
retention times, authentication credentials, log file location and rotation, and more) from a configuration file.

     
# Usage

``` backup.py [--help] [--log] [--version] config_file [sub_command ...]```
     
**supported sub_commands**: backup, backup-prune, check, forget, init, ls, password, prune, restore, stats, snapshots, unlock
    
 
# Example

```backup.py --log my-config.json backup-prune```
  
This will backup ALL paths configured in my-config.json using credentials (including AWS/GCP credentials) found
in the configuration, then prune those paths according to the forget-policy configured for each. Logs will go
to the configured location.

Example configuration files can be found in the config-examples directory.


# Features

- Single configuration file for: multiple target paths, password, excludes, backup dirs, logs etc
- Forget settings are configurable per project, or per path, in configuration json.
- Auto cleanup/rotation of logs.
- Packaging for easy installation/upgrade on remote hosts.
- Single execution from cron (does both backup and forget and/or prune)


# Installation
          
```package.sh``` creates restic-backup-vX.tar

Extracted contents of tar file will have this structure:
```text
    restic-backup/
        config/
        bin/
            backup.py
```

Create a key pair for the host and add to authorized_keys on restic host:

```ssh-keygen -t ed25519```

Create a cron script that invokes backup.py like so:
```shell
19 18 * * * /root/restic/bin/backup.py --log ../config/my-config.json backup-prune
```


## OSX setup

On OSX it may be necessary to grant `/usr/sbin/cron` "Full Disk Access" permission.  Settings -> 
Security & Privacy -> Full Disk Access.

## Upgrade
          
```shell
mv restic restic-old
tar -xvf restic-backup-v15.tar
```
Then copy any necessary credentials from the old directory and delete it.

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
