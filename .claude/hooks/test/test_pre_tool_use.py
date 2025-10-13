#!/usr/bin/env python3
"""
Test suite for pre_tool_use.py hook

Run with: uv run .claude/hooks/test/test_pre_tool_use.py
"""

import sys
import os
import json
from io import StringIO
import unittest

# Add parent directory to path to import pre_tool_use module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pre_tool_use import (
    is_dangerous_rm_command,
    is_dangerous_chained_command,
    is_alternative_deletion_method,
    is_dangerous_git_command,
    is_dangerous_permission_change,
    is_unauthorized_brew_command,
    is_credential_file_access,
)


class TestDangerousRmCommand(unittest.TestCase):
    """Test rm command detection"""

    def test_blocks_rm_rf(self):
        self.assertTrue(is_dangerous_rm_command("rm -rf /tmp/test"))
        self.assertTrue(is_dangerous_rm_command("rm -fr /tmp/test"))
        self.assertTrue(is_dangerous_rm_command("rm -Rf /tmp/test"))

    def test_blocks_rm_with_dangerous_paths(self):
        self.assertTrue(is_dangerous_rm_command("rm -r /"))
        self.assertTrue(is_dangerous_rm_command("rm -r ~"))
        self.assertTrue(is_dangerous_rm_command("rm -r ."))

    def test_allows_safe_rm(self):
        self.assertFalse(is_dangerous_rm_command("rm file.txt"))
        self.assertFalse(is_dangerous_rm_command("rm -f file.txt"))


class TestDangerousChainedCommand(unittest.TestCase):
    """Test chained command detection"""

    def test_blocks_chained_rm(self):
        self.assertTrue(is_dangerous_chained_command("ls && rm -rf /tmp"))
        self.assertTrue(is_dangerous_chained_command("test || rm -r /tmp"))
        self.assertTrue(is_dangerous_chained_command("echo foo; rm -rf /tmp"))

    def test_allows_safe_chained(self):
        self.assertFalse(is_dangerous_chained_command("ls && echo done"))
        self.assertFalse(is_dangerous_chained_command("make && npm test"))


class TestAlternativeDeletionMethod(unittest.TestCase):
    """Test alternative deletion methods"""

    def test_blocks_find_delete(self):
        self.assertTrue(is_alternative_deletion_method("find . -delete"))
        self.assertTrue(is_alternative_deletion_method("find . -exec rm -rf {} +"))

    def test_blocks_xargs_rm(self):
        self.assertTrue(is_alternative_deletion_method("ls | xargs rm"))

    def test_allows_safe_find(self):
        self.assertFalse(is_alternative_deletion_method("find . -name '*.txt'"))


class TestDangerousGitCommand(unittest.TestCase):
    """Test git command detection"""

    def test_blocks_force_push(self):
        self.assertTrue(is_dangerous_git_command("git push --force"))
        self.assertTrue(is_dangerous_git_command("git push -f"))
        self.assertTrue(is_dangerous_git_command("git push origin main --force"))

    def test_blocks_hard_reset(self):
        self.assertTrue(is_dangerous_git_command("git reset --hard HEAD~1"))

    def test_blocks_global_config(self):
        self.assertTrue(is_dangerous_git_command("git config --global user.name 'foo'"))

    def test_allows_safe_git(self):
        self.assertFalse(is_dangerous_git_command("git push"))
        self.assertFalse(is_dangerous_git_command("git commit -m 'test'"))
        self.assertFalse(is_dangerous_git_command("git status"))
        self.assertFalse(is_dangerous_git_command("git add ."))


class TestDangerousPermissionChange(unittest.TestCase):
    """Test permission change detection"""

    def test_blocks_chmod_777(self):
        self.assertTrue(is_dangerous_permission_change("chmod 777 file.txt"))
        self.assertTrue(is_dangerous_permission_change("chmod -R 777 /tmp"))

    def test_allows_chmod_plus_x(self):
        self.assertFalse(is_dangerous_permission_change("chmod +x script.sh"))

    def test_allows_safe_chmod(self):
        self.assertFalse(is_dangerous_permission_change("chmod 644 file.txt"))
        self.assertFalse(is_dangerous_permission_change("chmod 755 script.sh"))


class TestUnauthorizedBrewCommand(unittest.TestCase):
    """Test brew command detection"""

    def test_blocks_brew_install(self):
        self.assertTrue(is_unauthorized_brew_command("brew install python"))
        self.assertTrue(is_unauthorized_brew_command("brew uninstall python"))
        self.assertTrue(is_unauthorized_brew_command("brew upgrade"))

    def test_allows_brew_info(self):
        self.assertFalse(is_unauthorized_brew_command("brew list"))
        self.assertFalse(is_unauthorized_brew_command("brew search python"))


class TestCredentialFileAccess(unittest.TestCase):
    """Test credential file access detection"""

    def test_blocks_read_env_files(self):
        # Read tool
        self.assertTrue(is_credential_file_access('Read', {'file_path': '.env'}))
        self.assertTrue(is_credential_file_access('Read', {'file_path': '.env.local'}))
        self.assertTrue(is_credential_file_access('Read', {'file_path': '/path/to/.env'}))

    def test_allows_read_env_sample(self):
        self.assertFalse(is_credential_file_access('Read', {'file_path': '.env.sample'}))
        self.assertFalse(is_credential_file_access('Read', {'file_path': '.env.example'}))

    def test_blocks_bash_cat_env(self):
        self.assertTrue(is_credential_file_access('Bash', {'command': 'cat .env'}))
        self.assertTrue(is_credential_file_access('Bash', {'command': 'cat .env.local'}))
        self.assertTrue(is_credential_file_access('Bash', {'command': 'grep foo .env'}))

    def test_allows_bash_env_sample(self):
        self.assertFalse(is_credential_file_access('Bash', {'command': 'cat .env.sample'}))
        self.assertFalse(is_credential_file_access('Bash', {'command': 'cat .env.example'}))

    def test_allows_git_commit_with_env_mention(self):
        """Critical test: git commit messages should not be blocked"""
        self.assertFalse(is_credential_file_access('Bash', {
            'command': 'git commit -m "added foo to env"'
        }))
        self.assertFalse(is_credential_file_access('Bash', {
            'command': 'git commit -m "cat .env issue fixed"'
        }))
        self.assertFalse(is_credential_file_access('Bash', {
            'command': 'git add . && git commit -m "update environment"'
        }))

    def test_allows_git_operations(self):
        """Git operations should not be blocked"""
        self.assertFalse(is_credential_file_access('Bash', {'command': 'git add .'}))
        self.assertFalse(is_credential_file_access('Bash', {'command': 'git status'}))
        self.assertFalse(is_credential_file_access('Bash', {'command': 'git push'}))

    def test_allows_echo_with_env_mention(self):
        """Echo commands with .env in strings should not be blocked"""
        self.assertFalse(is_credential_file_access('Bash', {
            'command': 'echo "test .env"'
        }))
        self.assertFalse(is_credential_file_access('Bash', {
            'command': 'echo "Testing environment"'
        }))

    def test_blocks_vim_env(self):
        self.assertTrue(is_credential_file_access('Bash', {'command': 'vim .env'}))
        self.assertTrue(is_credential_file_access('Bash', {'command': 'nano .env'}))

    def test_blocks_credential_json_files(self):
        self.assertTrue(is_credential_file_access('Read', {'file_path': 'client_secret.json'}))
        self.assertTrue(is_credential_file_access('Read', {'file_path': '.credentials.json'}))
        self.assertTrue(is_credential_file_access('Bash', {'command': 'cat client_secret.json'}))

    def test_blocks_source_env(self):
        self.assertTrue(is_credential_file_access('Bash', {'command': 'source .env'}))
        self.assertTrue(is_credential_file_access('Bash', {'command': '. .env'}))


def run_tests():
    """Run all tests and print results"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "="*70)
    if result.wasSuccessful():
        print("✅ All tests passed!")
        return 0
    else:
        print(f"❌ {len(result.failures)} test(s) failed")
        print(f"❌ {len(result.errors)} test(s) had errors")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
