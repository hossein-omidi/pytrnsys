import dataclasses as _dc
import pathlib as _pl
import typing as _tp

import lark as _lark
import lark.visitors as _lvis

import pytrnsys.utils.result as _res
from . import _parse


@_dc.dataclass
class _ComputedVariable:  # pylint: disable=too-few-public-methods
    startIndex: int
    endIndex: int
    portProperty: str
    portName: str
    defaultVariableName: str

    def lengthChange(self, replacementString) -> int:
        lengthBeforeReplacing = self.endIndex - self.startIndex
        lengthAfterReplacing = len(replacementString)
        lengthChange = lengthAfterReplacing - lengthBeforeReplacing
        return lengthChange


class _CollectComputedVariables(_lvis.Visitor_Recursive):
    def __init__(self):
        super().__init__()

        self.computedVariables = []

    def computed_var(self, tree: _lark.Tree) -> None:  # pylint: disable=invalid-name
        portProperty = self._getChildToken("PORT_PROPERTY", tree)
        portName = self._getChildToken("PORT_NAME", tree)
        defaultVariableName = self._getChildToken("DEFAULT_VARIABLE_NAME", tree)
        computedVariable = _ComputedVariable(
            tree.meta.start_pos, tree.meta.end_pos, portProperty, portName, defaultVariableName
        )
        self.computedVariables.append(computedVariable)

    @staticmethod
    def _getChildToken(tokenType: str, tree: _lark.Tree) -> str:  # pylint: disable=invalid-name
        matchingChildTokens = [c for c in tree.children if isinstance(c, _lark.Token) and c.type == tokenType]

        if len(matchingChildTokens) != 1:
            raise ValueError(f"None or more than one token of type {tokenType} found.")

        matchingChildToken = matchingChildTokens[0]

        return matchingChildToken.value


def replaceComputedVariablesWithDefaults(inputDdckFilePath: _pl.Path) -> str:
    computedVariables = _getComputedVariablesSortedByStartIndexAscending(inputDdckFilePath)
    inputDdckContent = inputDdckFilePath.read_text()  # pylint: disable=bad-option-value,unspecified-encoding
    outputDdckContent = inputDdckContent
    offset = 0
    for computedVariable in computedVariables:
        replacementString = computedVariable.defaultVariableName
        outputDdckContent = _replace(
            outputDdckContent,
            offset + computedVariable.startIndex,
            offset + computedVariable.endIndex,
            replacementString,
        )
        offset += computedVariable.lengthChange(replacementString)
    return outputDdckContent


def replaceComputedVariablesWithName(inputDdckFilePath: _pl.Path, namesByPort: dict) -> _res.Result[str]:
    computedVariables = _getComputedVariablesSortedByStartIndexAscending(inputDdckFilePath)
    inputDdckContent = inputDdckFilePath.read_text()  # pylint: disable=bad-option-value,unspecified-encoding

    outputDdckContent = inputDdckContent
    offset = 0
    for computedVariable in computedVariables:
        namesForPort = namesByPort.get(computedVariable.portName, {})
        if _isEmpty(namesForPort):
            return _res.Error(
                f"There is no connection name in json file for {computedVariable.portName} for {inputDdckFilePath}"
            )

        replacementString = namesForPort.get(computedVariable.portProperty, {})
        if _isEmpty(replacementString):
            return _res.Error(
                f"There is no {computedVariable.portProperty} in json file for {computedVariable.portName} for "
                f"{inputDdckFilePath}"
            )

        outputDdckContent = _replace(
            outputDdckContent,
            offset + computedVariable.startIndex,
            offset + computedVariable.endIndex,
            replacementString,
        )
        offset += computedVariable.lengthChange(replacementString)

    return outputDdckContent


def _isEmpty(dictionary) -> bool:
    return not bool(dictionary)


def _getComputedVariablesSortedByStartIndexAscending(inputDdckFilePath: _pl.Path) -> _tp.Sequence["_ComputedVariable"]:
    tree = _parse.parseDdck(inputDdckFilePath)
    visitor = _CollectComputedVariables()
    visitor.visit(tree)

    sortedComputedVariables = sorted(visitor.computedVariables, key=lambda v: v.startIndex)

    currentAndNext = zip(sortedComputedVariables[:-1], sortedComputedVariables[1:])
    assert all(n.startIndex >= c.endIndex for c, n in currentAndNext)

    return sortedComputedVariables


def _replace(content: str, startIndex: int, endIndex: int, replacement: str) -> str:
    return content[:startIndex] + replacement + content[endIndex:]
