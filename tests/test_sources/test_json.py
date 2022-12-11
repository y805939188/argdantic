import json
from pathlib import Path
from typing import Any, Dict

import mock

from argdantic.sources.base import FileSettingsSource
from argdantic.testing import CLIRunner


def create_json_file(data: Dict[str, Any], path: Path) -> Path:
    path.write_text(json.dumps(data))
    return path


def test_json_no_import_error(tmp_path: Path) -> None:
    from argdantic.sources.json import JsonSettingsSource

    with mock.patch.dict("sys.modules", {"orjson": None}):
        path = create_json_file({"foo": "baz", "bar": 42}, tmp_path / "settings.json")
        source = JsonSettingsSource(path)
        assert isinstance(source, FileSettingsSource)
        assert source() == {"foo": "baz", "bar": 42}
        assert repr(source) == f"<JsonSettingsSource path={path}>"


def test_json_source(tmp_path: Path) -> None:
    from argdantic.sources.json import JsonSettingsSource

    path = create_json_file({"foo": "baz", "bar": 42}, tmp_path / "settings.json")
    source = JsonSettingsSource(path)
    assert isinstance(source, FileSettingsSource)
    assert source() == {"foo": "baz", "bar": 42}
    assert repr(source) == f"<JsonSettingsSource path={path}>"


def test_parser_using_json_source(tmp_path: Path, runner: CLIRunner) -> None:
    from argdantic import ArgParser
    from argdantic.sources.json import JsonSettingsSource

    path = create_json_file({"foo": "baz", "bar": 42}, tmp_path / "settings.json")
    parser = ArgParser()

    @parser.command(sources=[JsonSettingsSource(path)])
    def main(foo: str = None, bar: int = None) -> None:
        return foo, bar

    result = runner.invoke(parser, [])
    assert result.exception is None
    assert result.return_value == ("baz", 42)
