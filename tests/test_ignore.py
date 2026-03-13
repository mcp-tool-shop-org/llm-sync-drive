"""Tests for ignore-file parsing and pattern matching."""

from llm_sync_drive.ignore import BUILTIN_IGNORES, load_ignore_spec


class TestBuiltinIgnores:
    def test_git_ignored(self):
        assert ".git/" in BUILTIN_IGNORES

    def test_node_modules_ignored(self):
        assert "node_modules/" in BUILTIN_IGNORES

    def test_env_ignored(self):
        assert ".env" in BUILTIN_IGNORES

    def test_key_files_ignored(self):
        assert "*.key" in BUILTIN_IGNORES
        assert "*.pem" in BUILTIN_IGNORES


class TestLoadIgnoreSpec:
    def test_builtins_applied(self, tmp_path):
        spec = load_ignore_spec(tmp_path)
        assert spec.match_file(".git/config")
        assert spec.match_file("node_modules/foo/bar.js")
        assert spec.match_file("__pycache__/mod.pyc")
        assert spec.match_file(".env")

    def test_gitignore_loaded(self, tmp_path):
        (tmp_path / ".gitignore").write_text("build/\n*.tmp\n")
        spec = load_ignore_spec(tmp_path)
        assert spec.match_file("build/output.js")
        assert spec.match_file("data.tmp")
        assert not spec.match_file("src/main.py")

    def test_llmsignore_loaded(self, tmp_path):
        (tmp_path / ".llmsignore").write_text("fixtures/\n*.snap\n")
        spec = load_ignore_spec(tmp_path)
        assert spec.match_file("fixtures/big.json")
        assert spec.match_file("test.snap")

    def test_comments_and_blanks_skipped(self, tmp_path):
        (tmp_path / ".gitignore").write_text("# comment\n\n  \ndist/\n")
        spec = load_ignore_spec(tmp_path)
        assert spec.match_file("dist/bundle.js")
        # Comments should not become patterns
        assert not spec.match_file("# comment")

    def test_extra_patterns(self, tmp_path):
        spec = load_ignore_spec(tmp_path, extra_patterns=["*.log", "temp/"])
        assert spec.match_file("server.log")
        assert spec.match_file("temp/cache.dat")

    def test_no_ignore_files_still_works(self, tmp_path):
        spec = load_ignore_spec(tmp_path)
        # Only builtins apply
        assert not spec.match_file("src/main.py")
        assert spec.match_file(".env")
