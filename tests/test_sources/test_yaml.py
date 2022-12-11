from pathlib import Path
from typing import Any, Dict

import mock
import pytest

from argdantic.sources.base import FileSettingsSource
from argdantic.testing import CLIRunner


def create_yaml_file(data: Dict[str, Any], path: Path) -> Path:
    import yaml

    path.write_text(yaml.dump(data))
    return path


def test_yaml_import_error(tmp_path: Path) -> None:
    from argdantic.sources.yaml import YamlSettingsSource

    path = create_yaml_file({"foo": "baz", "bar": 42}, tmp_path / "settings.yaml")
    with mock.patch.dict("sys.modules", {"yaml": None}):
        source = YamlSettingsSource(path)
        assert repr(source) == f"<YamlSettingsSource path={path}>"
        assert isinstance(source, FileSettingsSource)
        with pytest.raises(ImportError):
            source()


def test_yaml_source(tmp_path: Path) -> None:
    from argdantic.sources.yaml import YamlSettingsSource

    path = create_yaml_file({"foo": "baz", "bar": 42}, tmp_path / "settings.yaml")
    source = YamlSettingsSource(path)
    assert repr(source) == f"<YamlSettingsSource path={path}>"
    assert isinstance(source, FileSettingsSource)
    assert source() == {"foo": "baz", "bar": 42}


def test_parser_using_yaml_source(tmp_path: Path, runner: CLIRunner) -> None:
    from argdantic import ArgParser
    from argdantic.sources.yaml import YamlSettingsSource

    path = create_yaml_file({"foo": "baz", "bar": 42}, tmp_path / "settings.yaml")
    parser = ArgParser()

    @parser.command(sources=[YamlSettingsSource(path)])
    def main(foo: str = None, bar: int = None) -> None:
        return foo, bar

    result = runner.invoke(parser, [])
    assert result.exception is None
    assert result.return_value == ("baz", 42)
