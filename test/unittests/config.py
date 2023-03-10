import os
import unittest

from restic.config import read_config

src_dir = os.path.dirname(os.path.abspath(__file__))
test_file_dir = f"{src_dir}/configs"


class ConfigTest(unittest.TestCase):

    def test_restic_path_abs(self):
        c = read_config(f'{test_file_dir}/unit-test-001.json', test_file_dir)
        self.assertEqual('../bin/restic-amd64', c.restic_path)
        self.assertEqual(os.path.normpath(f'{test_file_dir}/../bin/restic-amd64'), c.restic_path_abs())

    def test_restic_path_abs_with_abs_path_in_config_file(self):
        c = read_config(f'{test_file_dir}/unit-test-029.json', test_file_dir)
        self.assertEqual('/root/bin/restic-amd64', c.restic_path)
        self.assertEqual('/root/bin/restic-amd64', c.restic_path_abs())

    def test_log_directory_abs(self):
        c = read_config(f'{test_file_dir}/unit-test-001.json', test_file_dir)
        self.assertEqual('../logs/example-osx', c.log_directory)
        self.assertEqual(os.path.normpath(f'{test_file_dir}/../logs/example-osx'), c.log_directory_abs())

    def test_log_directory_abs_with_abs_path_in_config_file(self):
        c = read_config(f'{test_file_dir}/unit-test-030.json', test_file_dir)
        self.assertEqual('/home/user/bob/logs', c.log_directory)
        self.assertEqual('/home/user/bob/logs', c.log_directory_abs())

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def test_one_good_config(self):
        c = read_config(f'{test_file_dir}/unit-test-001.json', None)
        self.assertEqual('sftp:restic@dev.redshiftsoft.com:restic-repos/test-repo-osx', c.repository)
        self.assertEqual('../logs/example-osx', c.log_directory)
        self.assertEqual(128, c.log_retention_days)
        self.assertEqual('abc!d-1234-24^3fvf-ae*3343', c.password)
        self.assertEqual(["--keep-daily", "7", "--keep-weekly", "5", "--keep-monthly", "12"], c.forget_policy)
        self.assertEqual(0.65, c.prune_policy)
        env = c.environment
        self.assertTrue(isinstance(env, dict))
        self.assertTrue(len(env) == 3)
        self.assertEqual('value1', env['key1'])
        self.assertEqual('value2', env['key2'])
        self.assertEqual('value3', env['key3'])
        self.assertEqual(6, len(c.backup_paths))
        self.assertEqual(".DS_Store", c.backup_paths[0].excludes[0].pattern)
        self.assertEqual("dbeaver", c.backup_paths[0].excludes[1].pattern)
        # backup-commands
        commands = c.backup_commands
        self.assertEqual(2, len(commands))
        self.assertEqual(commands[0].command, ["ls", "-lat", "/Users/keith"])
        self.assertEqual(commands[0].repo_path, "/ls-lat-users.txt")
        self.assertEqual(commands[1].command, ["rm", "-r", "/tmp/keith/stuff"])
        self.assertEqual(commands[1].repo_path, "/rm-r-tmp.txt")
        # restic-path
        self.assertEqual(c.restic_path, '../bin/restic-amd64')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def test_all_real_configs_valid(self):
        config_dir = f"{src_dir}/../../config/"
        self.assertTrue(os.path.isdir(config_dir))
        config_count = 0
        for root, dirs, files in os.walk(config_dir):
            for file in files:
                read_config(os.path.join(root, file), None)
                config_count = config_count + 1
        self.assertTrue(config_count >= 8)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def test_bad_property_in_top_level(self):
        with self.assertRaisesRegex(ValueError, "invalid property: 'foobar'"):
            read_config(f'{test_file_dir}/unit-test-002.json', None)

    def test_bad_property_in_backup_path_level(self):
        with self.assertRaisesRegex(ValueError, "invalid property: 'invalid-backup-path-prop'"):
            read_config(f'{test_file_dir}/unit-test-003.json', None)

    def test_bad_property_in_excludes_level(self):
        with self.assertRaisesRegex(ValueError, "invalid property: 'bad-exclude-prop'"):
            read_config(f'{test_file_dir}/unit-test-004.json', None)

    def test_duplicate_path(self):
        with self.assertRaisesRegex(ValueError, "duplicate path value: '/foo/bar'"):
            read_config(f'{test_file_dir}/unit-test-005.json', None)

    def test_duplicate_exclude_pattern(self):
        with self.assertRaisesRegex(ValueError, "duplicate exclude path: 'pattern2'"):
            read_config(f'{test_file_dir}/unit-test-006.json', None)

    def test_missing_backup_paths(self):
        with self.assertRaisesRegex(ValueError, "no backup paths or commands defined"):
            read_config(f'{test_file_dir}/unit-test-007.json', None)

    def test_invalid_type_in_excludes(self):
        with self.assertRaisesRegex(ValueError, "unexpected type for exclude element: <class 'int'>"):
            read_config(f'{test_file_dir}/unit-test-008.json', None)

    def test_empty_list_global_forget_policy(self):
        c = read_config(f'{test_file_dir}/unit-test-009.json', None)
        self.assertIsNone(c.forget_policy)

    def test_missing_global_forget_policy(self):
        c = read_config(f'{test_file_dir}/unit-test-010.json', None)
        self.assertIsNone(c.forget_policy)

    def test_empty_list_path_level_forget_policy(self):
        c = read_config(f'{test_file_dir}/unit-test-011.json', None)
        self.assertIsNone(c.backup_paths[0].forget_policy)

    def test_missing_path_level_forget_policy(self):
        c = read_config(f'{test_file_dir}/unit-test-012.json', None)
        self.assertIsNone(c.backup_paths[0].forget_policy)

    def test_invalid_empty_password(self):
        with self.assertRaisesRegex(ValueError, "value for 'password' cannot be empty"):
            read_config(f'{test_file_dir}/unit-test-013.json', None)

    def test_invalid_empty_repository(self):
        with self.assertRaisesRegex(ValueError, "value for 'repository' cannot be empty"):
            read_config(f'{test_file_dir}/unit-test-014.json', None)

    def test_invalid_empty_log_directory(self):
        with self.assertRaisesRegex(ValueError, "value for 'log-directory' cannot be empty"):
            read_config(f'{test_file_dir}/unit-test-015.json', None)

    def test_invalid_empty_exclude_pattern(self):
        with self.assertRaisesRegex(ValueError, "exclude pattern can not be empty"):
            read_config(f'{test_file_dir}/unit-test-016.json', None)

    def test_invalid_environment_type(self):
        with self.assertRaisesRegex(ValueError, "environment must have keys and values"):
            read_config(f'{test_file_dir}/unit-test-017.json', None)

    def test_default_prune_policy(self):
        c = read_config(f'{test_file_dir}/unit-test-018.json', None)
        self.assertEqual(0.0, c.prune_policy)

    def test_invalid_prune_policy_small(self):
        with self.assertRaisesRegex(ValueError, "prune-policy must be \\[0,1\\] probability of running prune"):
            read_config(f'{test_file_dir}/unit-test-019.json', None)

    def test_invalid_prune_policy_big(self):
        with self.assertRaisesRegex(ValueError, "prune-policy must be \\[0,1\\] probability of running prune"):
            read_config(f'{test_file_dir}/unit-test-020.json', None)

    def test_default_log_retention_days(self):
        c = read_config(f'{test_file_dir}/unit-test-021.json', None)
        self.assertEqual(365 * 2, c.log_retention_days)

    def test_invalid_commands_property(self):
        with self.assertRaisesRegex(ValueError, "invalid property: 'path'"):
            read_config(f'{test_file_dir}/unit-test-022.json', None)

    def test_invalid_type_for_command_prop_command(self):
        with self.assertRaisesRegex(ValueError, "expected command to be a list"):
            read_config(f'{test_file_dir}/unit-test-023.json', None)

    def test_invalid_type_for_command_prop_repo_path(self):
        with self.assertRaisesRegex(ValueError, "expected repo-path to be a string"):
            read_config(f'{test_file_dir}/unit-test-024.json', None)

    def test_invalid_empty_value_command_array(self):
        with self.assertRaisesRegex(ValueError, "expected command list to have at least one element"):
            read_config(f'{test_file_dir}/unit-test-025.json', None)

    def test_invalid_command_repo_path(self):
        with self.assertRaisesRegex(ValueError, "repo path for commands must start with forward slash"):
            read_config(f'{test_file_dir}/unit-test-026.json', None)

    def test_invalid_restic_path_empty(self):
        with self.assertRaisesRegex(ValueError, "expected a non-empty value for restic-path"):
            read_config(f'{test_file_dir}/unit-test-027.json', None)

    def test_invalid_restic_path_type(self):
        with self.assertRaisesRegex(ValueError, "expected restic-path to be a string"):
            read_config(f'{test_file_dir}/unit-test-028.json', None)
