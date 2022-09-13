import dataclasses as _dc
import json as _json
import pathlib as _pl
import typing as _tp

import pytest as _pt

import pytrnsys.ddck.replaceTokens as _replace
import pytrnsys.utils.result as _res

_REPLACE_WITH_DEFAULTS_DATA_DIR = _pl.Path(__file__).parent / "defaults"
_REPLACE_WITH_NAMES_DATA_DIR = _pl.Path(__file__).parent / "names"


class _Paths:  # pylint: disable=too-few-public-methods
    def __init__(self, projectDirPath: _pl.Path) -> None:
        self.actualDdckDirPath = projectDirPath / "actual"
        self.inputDirPath = projectDirPath / projectDirPath.name
        self.inputDdckDirPath = self.inputDirPath / "ddck"
        self.expectedDdckDirPath = projectDirPath / "expected"

        self.ddckPlaceHolderValuesFilePath = self.inputDirPath / "DdckPlaceHolderValues.json"


@_dc.dataclass
class _DdckFile:  # pylint: disable=too-few-public-methods
    projectDirPath: _pl.Path
    ddckPlaceHoldervaluesFilePath: _pl.Path
    componentName: str

    input: _pl.Path
    actual: _pl.Path
    expected: _pl.Path

    @property
    def testId(self) -> str:
        relativeInputPath = self.input.relative_to(self.projectDirPath)
        return relativeInputPath.as_posix()


def getDdckFiles() -> _tp.Iterable[_DdckFile]:
    for projectDirPath in _REPLACE_WITH_NAMES_DATA_DIR.iterdir():
        assert projectDirPath.is_dir()

        paths = _Paths(projectDirPath)

        inputDdckFilesPaths = paths.inputDdckDirPath.rglob("*.ddck")

        for inputDdckFilePath in inputDdckFilesPaths:
            relativeDdckFilePath = inputDdckFilePath.relative_to(paths.inputDdckDirPath)

            actualDdckFilePath = paths.actualDdckDirPath / relativeDdckFilePath
            expectedDdckFilePath = paths.expectedDdckDirPath / relativeDdckFilePath

            componentName = inputDdckFilePath.parent.name

            yield _DdckFile(
                projectDirPath,
                paths.ddckPlaceHolderValuesFilePath,
                componentName,
                inputDdckFilePath,
                actualDdckFilePath,
                expectedDdckFilePath,
            )


_REPLACE_WITH_NAME_TEST_CASES = [_pt.param(p, id=p.testId) for p in getDdckFiles()]


class TestDdckGeneration:
    @staticmethod
    def testReplaceTokensWithDefaults():
        inputDdckFilePath = _REPLACE_WITH_DEFAULTS_DATA_DIR / "type977_v1_input.ddck"
        expectedDdckFilePath = _REPLACE_WITH_DEFAULTS_DATA_DIR / "type977_v1_expected.ddck"
        actualDdckContent = _replace.replaceTokensWithDefaults(inputDdckFilePath)
        assert actualDdckContent == expectedDdckFilePath.read_text()

    @staticmethod
    def testReplaceTokensWithDefaultsMissingInputVariableDefaults():
        inputDdckFilePath = _REPLACE_WITH_DEFAULTS_DATA_DIR / "type977_v1_input_missing_default.ddck"
        result = _replace.replaceTokensWithDefaults(inputDdckFilePath)
        assert _res.isError(result)
        error = _res.error(result)
        print(error.message)
        assert error.message == """\
No placeholder values were provided and the computed variables at the following location
(line number: column number) don't have default values in the file type977_v1_input_missing_default.ddck:
\t26:14
\t27:13
\t28:15
"""

    @staticmethod
    @_pt.mark.parametrize("ddckFile", _REPLACE_WITH_NAME_TEST_CASES)
    def testReplaceTokens(ddckFile: _DdckFile):
        serializedDdckPlaceHolderValues = ddckFile.ddckPlaceHoldervaluesFilePath.read_text(encoding="utf8")
        ddckPlaceHolderValues = _json.loads(serializedDdckPlaceHolderValues)

        names = ddckPlaceHolderValues.get(ddckFile.componentName) or {}

        result = _replace.replaceTokens(ddckFile.input, ddckFile.componentName, names)
        _res.throwIfError(result)
        actualDdckContent = _res.value(result)

        ddckFile.actual.parent.mkdir(parents=True, exist_ok=True)
        ddckFile.actual.write_text(actualDdckContent)

        assert ddckFile.actual.read_text() == ddckFile.expected.read_text(encoding="windows-1252")
