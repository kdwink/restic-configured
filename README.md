# restic-backup

## Improvements

- [ ] Single execution from cron (does both backup and forget and/or prune)
- [ ] Auto cleanup/rotation of logs.
- [ ] Ability to execute arbitrary command for other repos.
- [x] Make redirect of output optional command line arg.
- [x] Validate config file. Assert required fields and error on unrecognized fields.
- [x] Singe configuration file for: password, excludes, and backup dirs
- [x] Forget settings are configurable per project in config json.
- [x] Ability to more easily execute arbitrary restic commands.



## switch

[ ] keith-desktop
[x] kdwink-mac
[ ] dev
[x] xiujia-pc
[ ] forum01.supercharge.info
[ ] super01.supercharge.info
[ ] keithfabryorders.com 


## notes

Forget and prune are separate commands to allow the use case where several machines might all sync to the same
repository and only issue forget commands, possibly each with a unique policy, while a single machine, possibly
close to the repository, issues the prune command.

### Pattern matching:

* https://restic.readthedocs.io/en/latest/040_backup.html#excluding-files
* Pattern is matched against entire file path.
* Trailing / in pattern is ignored, leading / anchors pattern to root directory.
* Pattern must match one or more complete file/directory components of path.
* Single * wildcard does NOT match over directory separator
