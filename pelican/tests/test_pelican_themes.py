import pytest

from pelican.tools import pelican_themes


@pytest.fixture
def theme_paths(tmp_path, monkeypatch):
    themes_dir = tmp_path / "themes"
    themes_dir.mkdir()
    theme_dir = themes_dir / "mytheme"
    theme_dir.mkdir()
    (theme_dir / "template.html").write_text("theme content", encoding="utf-8")
    victim_dir = tmp_path / "victim"
    victim_dir.mkdir()
    (victim_dir / "keep.txt").write_text("keep me", encoding="utf-8")
    monkeypatch.setattr(pelican_themes, "_THEMES_PATH", str(themes_dir))
    return themes_dir, theme_dir, victim_dir


@pytest.mark.parametrize(
    "theme_name",
    ["..", ".", "../victim", "..\\victim", "", "my/theme", "my\\theme"],
)
def test_remove_rejects_invalid_names(theme_name, theme_paths, capsys):
    themes_dir, theme_dir, victim_dir = theme_paths

    assert pelican_themes.remove(theme_name) is None

    assert themes_dir.is_dir()
    assert theme_dir.is_dir()
    assert (theme_dir / "template.html").read_text(encoding="utf-8") == "theme content"
    assert victim_dir.is_dir()
    assert (victim_dir / "keep.txt").read_text(encoding="utf-8") == "keep me"
    assert "Invalid theme name" in capsys.readouterr().err


def test_remove_theme_directory(theme_paths, capsys):
    themes_dir, theme_dir, victim_dir = theme_paths

    assert pelican_themes.remove("mytheme") is None

    assert not theme_dir.exists()
    assert themes_dir.is_dir()
    assert victim_dir.is_dir()
    assert not capsys.readouterr().err


@pytest.mark.parametrize("theme_name", ["simple", "notmyidea"])
def test_remove_refuses_builtin_theme(theme_name, theme_paths, capsys):
    themes_dir, theme_dir, victim_dir = theme_paths
    builtin_dir = themes_dir / theme_name
    builtin_dir.mkdir()

    assert pelican_themes.remove(theme_name) is None

    assert builtin_dir.is_dir()
    assert theme_dir.is_dir()
    assert victim_dir.is_dir()
    assert "is a builtin theme" in capsys.readouterr().err


@pytest.mark.parametrize("broken", [False, True])
def test_remove_symlink_preserves_target(theme_paths, broken, capsys):
    themes_dir, theme_dir, victim_dir = theme_paths
    link = themes_dir / "linkedtheme"
    target = victim_dir / "missing" if broken else victim_dir
    try:
        link.symlink_to(target, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("Creating symlinks is not supported")

    assert pelican_themes.remove("linkedtheme") is None

    assert not link.is_symlink()
    assert themes_dir.is_dir()
    assert theme_dir.is_dir()
    assert victim_dir.is_dir()
    assert (victim_dir / "keep.txt").read_text(encoding="utf-8") == "keep me"
    assert not capsys.readouterr().err


def test_remove_missing_theme(theme_paths, capsys):
    themes_dir, theme_dir, victim_dir = theme_paths

    assert pelican_themes.remove("missing") is None

    assert themes_dir.is_dir()
    assert theme_dir.is_dir()
    assert victim_dir.is_dir()
    assert "no such file or directory" in capsys.readouterr().err


@pytest.mark.parametrize("target_name", ["themes", "victim", "themes-other"])
def test_remove_rejects_target_outside_root(
    theme_paths, target_name, monkeypatch, capsys
):
    themes_dir, theme_dir, victim_dir = theme_paths
    resolved_target = str(themes_dir.parent / target_name)
    abspath = pelican_themes.os.path.abspath

    def resolve_target(path):
        if path == str(theme_dir):
            return resolved_target
        return abspath(path)

    monkeypatch.setattr(pelican_themes.os.path, "abspath", resolve_target)

    assert pelican_themes.remove("mytheme") is None

    assert themes_dir.is_dir()
    assert theme_dir.is_dir()
    assert victim_dir.is_dir()
    assert "must be inside the themes directory" in capsys.readouterr().err


def test_remove_rejects_incomparable_paths(theme_paths, monkeypatch, capsys):
    themes_dir, theme_dir, victim_dir = theme_paths

    def incompatible_paths(_paths):
        raise ValueError("Paths are on different drives")

    monkeypatch.setattr(pelican_themes.os.path, "commonpath", incompatible_paths)

    assert pelican_themes.remove("mytheme") is None

    assert themes_dir.is_dir()
    assert theme_dir.is_dir()
    assert victim_dir.is_dir()
    assert "must be inside the themes directory" in capsys.readouterr().err
