import unittest
import json
import restic.config
import os


def read_config_json(file):
    src_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{src_dir}/{file}", 'rb') as f:
        read_bytes = f.read()
        json_string = read_bytes.decode('utf-8')
        return json.loads(json_string)


def read_config(file):
    config_dict = read_config_json(file)
    return restic.config.Configuration(config_dict)


class ConfigTest(unittest.TestCase):

    def test_config(self):
        c = read_config('unit-test-001.json')
        self.assertEqual('sftp:restic@dev.redshiftsoft.com:restic-repos/test-repo-osx', c.repository)
        self.assertEqual('logs/example-osx', c.log_directory)
        self.assertEqual(["--keep-daily", "7", "--keep-weekly", "5", "--keep-monthly", "12"], c.forget_policy)
        self.assertEqual(6, len(c.backup_paths))
        self.assertEqual(".DS_Store", c.backup_paths[0].excludes[0].pattern)
        self.assertEqual("dbeaver", c.backup_paths[0].excludes[1].pattern)

    def test_bad_property_in_top_level(self):
        with self.assertRaisesRegex(ValueError, "invalid property: 'foobar'"):
            read_config('unit-test-002.json')

    def test_bad_property_in_backup_path_level(self):
        with self.assertRaisesRegex(ValueError, "invalid property: 'invalid-backup-path-prop'"):
            read_config('unit-test-003.json')

    def test_bad_property_in_excludes_level(self):
        with self.assertRaisesRegex(ValueError, "invalid property: 'bad-exclude-prop'"):
            read_config('unit-test-004.json')

    def test_duplicate_path(self):
        with self.assertRaisesRegex(ValueError, "duplicate path value: '/foo/bar'"):
            read_config('unit-test-005.json')

    def test_duplicate_exclude_pattern(self):
        with self.assertRaisesRegex(ValueError, "duplicate exclude path: 'pattern2'"):
            read_config('unit-test-006.json')
