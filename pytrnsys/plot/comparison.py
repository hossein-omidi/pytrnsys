__all__ = ['createPlot']

import json as _json
import os as _os
import pathlib as _pl
import typing as _tp
import dataclasses as _dc

import matplotlib.pyplot as _plt
import numpy as _np

import pytrnsys.psim.conditions as _conds
import pytrnsys.report.latexReport as _latex
import pytrnsys.utils.uncertainFloat as _uf


def createPlot(plotVariables, pathFolder, typeOfProcess, logger, latexNames, configPath,
               stylesheet, plotStyle, comparePlotUserName, setPrintDataForGle, shallPlotUncertainties):
    xAxisVariable, yAxisVariable, seriesVariable, chunkVariable, conditions = \
        _separatePlotVariables(plotVariables)

    resultFilePaths = _getResultsFilePaths(pathFolder, typeOfProcess)
    if not resultFilePaths:
        logger.error('No results.json-files found.')
        logger.error('Unable to generate "comparePlot %s %s %s"',
                     xAxisVariable, yAxisVariable, seriesVariable)
        return

    values = _loadValues(resultFilePaths, xAxisVariable, yAxisVariable, seriesVariable, chunkVariable, conditions)
    if not values:
        logger.warning('The following conditions from "comparePlotConditional" were never met all at once:')
        for condition in conditions.conditions:
            logger.warning(condition)
        logger.warning('The respective plot cannot be generated.')
        return

    _configurePypltStyle(stylesheet)

    styles = ['x-', 'x--', 'x-.', 'x:', 'o-', 'o--', 'o-.', 'o:']
    if plotStyle == "dot":
        styles = ['x', 'o', '+', 'd', 's', 'v', '^', 'h']

    if len(values) > len(styles):
        raise AssertionError("Too many chunks")

    seriesColors = _getSeriesColors(values)

    doc = _createLatexDoc(configPath, latexNames)

    fig, ax = _plt.subplots(constrained_layout=True)

    chunkLabels, dummyLines = _plotValues(ax, values, shallPlotUncertainties, seriesColors, styles, doc)

    _setLegendsAndLabels(fig, ax, xAxisVariable, yAxisVariable, seriesVariable, chunkVariable,
                         chunkLabels, dummyLines, doc)

    conditionsFileNamePart, conditionsTitle = _getConditionsFileNameAndTitle(conditions)

    if conditionsTitle:
        ax.set_title(conditionsTitle)

    _savePlotAndData(fig, xAxisVariable, yAxisVariable, seriesVariable, chunkVariable, pathFolder, comparePlotUserName,
                     conditionsFileNamePart, values, setPrintDataForGle, shallPlotUncertainties)


def _separatePlotVariables(plotVariables):
    if len(plotVariables) < 2:
        raise ValueError('You did not specify variable names and labels '
                         'for the x and the y Axis in a compare Plot line')
    xAxisVariable = plotVariables[0]
    yAxisVariable = plotVariables[1]

    seriesVariable = ''
    chunkVariable = ''

    serializedConditions = plotVariables[2:]
    if len(plotVariables) >= 3 and not _conds.mayBeSerializedCondition(plotVariables[2]):
        seriesVariable = plotVariables[2]
        serializedConditions = plotVariables[3:]

    if len(plotVariables) >= 4 and not _conds.mayBeSerializedCondition(plotVariables[3]):
        chunkVariable = plotVariables[3]
        serializedConditions = plotVariables[4:]

    conditions = _conds.createConditions(serializedConditions)

    return xAxisVariable, yAxisVariable, seriesVariable, chunkVariable, conditions


def _getResultsFilePaths(pathFolder, typeOfProcess) -> _tp.Sequence[_pl.Path]:
    pathFolder = _pl.Path(pathFolder)
    pattern = "*-results.json"

    if typeOfProcess == "json":
        return list(pathFolder.rglob(pattern))

    return list(pathFolder.glob(pattern))


def _loadValues(resultFilePaths, xAxisVariable, yAxisVariable, seriesVariable, chunkVariable, conditions) \
        -> _tp.Dict[str, _tp.Dict[str, _tp.Sequence[float]]]:
    values = {}
    for resultFilePath in resultFilePaths:
        results = _loadResults(resultFilePath)

        conditionsFulfilled = conditions.doResultsSatisfyConditions(results)
        if not conditionsFulfilled:
            continue

        xAxis = _getValue(results, xAxisVariable)
        yAxis = _getValue(results, yAxisVariable)

        chunkVariableValue = results[chunkVariable] if chunkVariable else None
        if chunkVariableValue not in values:
            values[chunkVariableValue] = {}
        chunk = values[chunkVariableValue]

        seriesVariableValue = results[seriesVariable] if seriesVariable else None
        if seriesVariableValue not in chunk:
            chunk[seriesVariableValue] = []
        seriesValues = chunk[seriesVariableValue]

        seriesValues.append((xAxis, yAxis))

    return values


def _loadResults(resultFilePath) -> _tp.Dict[str, _tp.Any]:
    serializedResults = resultFilePath.read_text()
    resultsDict = _json.loads(serializedResults)
    return resultsDict


def _getValue(resultsDict, variable):
    if '[' not in variable:
        yAxis = resultsDict[variable]
    else:
        name, index = str(variable).split('[')
        index = int(index.replace(']', ''))
        yAxis = resultsDict[name][index]
    return yAxis


def _configurePypltStyle(stylesheet):
    if not stylesheet:
        stylesheet = 'word.mplstyle'
    if stylesheet not in _plt.style.available:
        root = _os.path.dirname(_os.path.abspath(__file__))
        stylesheet = _os.path.join(root, r"..\\plot\\stylesheets", stylesheet)
    _plt.style.use(stylesheet)


def _plotValues(ax: _plt.Axes, values, shallPlotUncertainties, seriesColors, styles, doc):
    dummyLines = []
    chunkLabels = []
    seriesLabels = set()
    for chunkVariableValue, style in zip(values, styles):
        dummyLines.append(ax.plot([], [], style, c='black'))
        chunkLabel = _getChunkLabel(chunkVariableValue)

        if chunkLabel:
            chunkLabels.append(chunkLabel)

        chunk = values[chunkVariableValue]
        for seriesVariableValue in chunk:
            series = chunk[seriesVariableValue]

            xs, xerrors, ys, yerrors = _getXAndYValuesAndErrorsOrderedByXValues(series)

            label = _getSeriesLabelOrNone(seriesVariableValue, seriesLabels, doc)

            if shallPlotUncertainties:
                ax.errorbar(xs, ys, yerrors.transpose(), xerrors.transpose(),
                            style, color=seriesColors[seriesVariableValue], label=label)
            else:
                ax.plot(xs, ys, style, color=seriesColors[seriesVariableValue], label=label)

    return chunkLabels, dummyLines


def _getXAndYValuesAndErrorsOrderedByXValues(series) -> _tp.Tuple[_np.ndarray, _np.ndarray, _np.ndarray, _np.ndarray]:
    xs, ys = zip(*series)

    xValues, xErrors = _getValuesAndErrors(xs)
    yValues, yErrors = _getValuesAndErrors(ys)

    indices = _np.argsort(xValues)

    return xValues[indices], xErrors[indices], yValues[indices], yErrors[indices]


def _getValuesAndErrors(us):
    if not _haveValuesErrors(us):
        errors = [(0, 0) for _ in us]
        return _np.array(us), _np.array(errors)

    us = [_uf.UncertainFloat.from_dict(u) for u in us]

    values = [u.mean for u in us]
    errors = [(-u.toLowerBound, u.toUpperBound) for u in us]

    return _np.array(values), _np.array(errors)


def _haveValuesErrors(us):
    return any(isinstance(u, dict) for u in us)


def _createLatexDoc(configPath, latexNames):
    doc = _latex.LatexReport('', '')
    if latexNames:
        if ':' in latexNames:
            latexNameFullPath = latexNames
        else:
            latexNameFullPath = _os.path.join(configPath, latexNames)
        doc.getLatexNamesDict(file=latexNameFullPath)
    else:
        doc.getLatexNamesDict()
    return doc


def _getSeriesColors(values):
    colors = _plt.rcParams['axes.prop_cycle'].by_key()['color']
    series = {s for (c, vs) in values.items() for s in vs}
    seriesColors = {s: colors[i % len(colors)] for i, s in enumerate(series)}
    return seriesColors


def _getChunkLabel(chunkVariableValue):
    if chunkVariableValue is None:
        return None

    if isinstance(chunkVariableValue, str):
        return chunkVariableValue

    roundedValue = round(float(chunkVariableValue), 2)
    return "{:.2f}".format(roundedValue)


def _getSeriesLabelOrNone(seriesVariableValue, labelSet, doc):
    if seriesVariableValue is None:
        return None

    labelValue = seriesVariableValue if isinstance(seriesVariableValue, str) \
        else round(float(seriesVariableValue), 2)

    if labelValue in labelSet:
        return None

    labelSet.add(labelValue)

    if not isinstance(labelValue, str):
        label = "{0:.1f}".format(labelValue)
    else:
        label = doc.getNiceLatexNames(labelValue)

    return label


def _setLegendsAndLabels(fig, ax, xAxisVariable, yAxisVariable, seriesVariable, chunkVariable, chunkLabels, dummyLines,
                         doc):
    if chunkVariable:
        legend = fig.legend([dummy_line[0] for dummy_line in dummyLines], chunkLabels,
                            title=doc.getNiceLatexNames(chunkVariable), bbox_to_anchor=(1.31, 1.0),
                            bbox_transform=ax.transAxes)
        fig.add_artist(legend)
    if seriesVariable:
        legend = fig.legend(title=doc.getNiceLatexNames(seriesVariable), bbox_to_anchor=(1.15, 1.0),
                            bbox_transform=ax.transAxes)
        fig.add_artist(legend)
    ax.set_xlabel(doc.getNiceLatexNames(xAxisVariable))
    ax.set_ylabel(doc.getNiceLatexNames(yAxisVariable))


def _savePlotAndData(fig, xAxisVariable, yAxisVariable, seriesVariable, chunkVariable, pathFolder, comparePlotUserName,
                     conditionsFileNamePart, values, setPrintDataForGle, shallPlotUncertainties):
    fileName = _getFileName(xAxisVariable, yAxisVariable, seriesVariable,
                            chunkVariable, conditionsFileNamePart, comparePlotUserName)

    fig.savefig(_os.path.join(pathFolder, fileName + '.png'), bbox_inches='tight')
    _plt.close()

    if setPrintDataForGle:
        _doPrintDataForGle(pathFolder, fileName, values, xAxisVariable, yAxisVariable,
                           seriesVariable, chunkVariable, shallPlotUncertainties)


def _getFileName(xAxisVariable, yAxisVariable, seriesVariable, chunkVariable, conditionsFileName, comparePlotUserName):
    possibleParts = [
        xAxisVariable,
        yAxisVariable,
        seriesVariable,
        chunkVariable,
        conditionsFileName,
        comparePlotUserName
    ]

    parts = [part for part in possibleParts if part]

    return "_".join(parts)


def _getConditionsFileNameAndTitle(conditions):
    conditionsFileName = ''
    conditionsTitle = ''
    for condition in conditions.conditions:
        conditionsFileName += condition.serializedCondition
        if conditionsTitle != '':
            conditionsTitle += ', ' + condition.serializedCondition
        else:
            conditionsTitle += condition.serializedCondition
    conditionsTitle = conditionsTitle.replace('RANGE', '')
    conditionsTitle = conditionsTitle.replace('LIST', '')
    conditionsFileName = conditionsFileName.replace('==', '=')
    conditionsFileName = conditionsFileName.replace('>', '_g_')
    conditionsFileName = conditionsFileName.replace('<', '_l_')
    conditionsFileName = conditionsFileName.replace('>=', '_ge_')
    conditionsFileName = conditionsFileName.replace('<=', '_le_')
    conditionsFileName = conditionsFileName.replace('|', '_o_')
    conditionsFileName = conditionsFileName.replace('RANGE:', '')
    conditionsFileName = conditionsFileName.replace('LIST:', '')
    return conditionsFileName, conditionsTitle


def _doPrintDataForGle(pathFolder, fileName, values, abscissaVariable, ordinateVariable, seriesVariable, chunkVariable,
                       shallPlotUncertainties):
    allSeries = _Series.fromValues(abscissaVariable, ordinateVariable, seriesVariable,
                                   chunkVariable, values, shallPlotUncertainties)

    columnHeadersLegend = _getColumnHeadersLegend(abscissaVariable, ordinateVariable, seriesVariable, chunkVariable)
    columnHeaders = "\t".join(f"{s.getAbscissaHeader()}\t{s.getOrdinateHeader()}" for s in allSeries)

    lines = f"! {columnHeadersLegend}\n! {columnHeaders}\n"
    maxSeriesLength = max(s.length for s in allSeries)
    for rowIndex in range(maxSeriesLength):
        for series in allSeries:
            if series.length <= rowIndex:
                lines += "-\t"
                continue

            x, xMax, xMin = _getMinMeanMaxAt(series.abscissa, rowIndex)
            formattedX = _formatUncertainValue(xMin, x, xMax, shallPlotUncertainties)

            yMin, y, yMax = _getMinMeanMaxAt(series.ordinate, rowIndex)
            formattedY = _formatUncertainValue(yMin, y, yMax, shallPlotUncertainties)

            lines += f"{formattedX}\t{formattedY}"

        lines += "\n"

        datFilePath = _pl.Path(pathFolder) / f"{fileName}.dat"
        datFilePath.write_text(lines)


def _getMinMeanMaxAt(axisValues, rowIndex):
    uMin, u, uMax = axisValues.mins[rowIndex], axisValues.means[rowIndex], axisValues.maxs[rowIndex]
    return uMin, u, uMax


@_dc.dataclass()
class _Series:
    index: _tp.Optional[int]
    series: _tp.Optional["_GroupingValue"]
    chunk: _tp.Optional["_GroupingValue"]

    abscissa: "_AxisValues"
    ordinate: "_AxisValues"

    shallPrintUncertainties: bool

    @classmethod
    def fromValues(cls, abscissaVariable, ordinateVariable, seriesVariable,
                   chunkVariable, values, shallPrintUncertainties):
        if not seriesVariable:
            valuesForSeries = values[None][None]

            abscissaValues, ordinateValues = \
                cls._createAbscissaAndOrdinateAxisValues(abscissaVariable, ordinateVariable, valuesForSeries)

            series = _Series(index=None, series=None, chunk=None, abscissa=abscissaValues,
                             ordinate=ordinateValues, shallPrintUncertainties=shallPrintUncertainties)
            return [series]

        if not chunkVariable:
            allSeries = []
            for seriesValue, valuesForSeries in values[None].items():
                i = len(allSeries) + 1
                seriesGroupingValue = _GroupingValue(seriesVariable, seriesValue)
                chunkGroupingValue = None

                abscissaValues, ordinateValues = \
                    cls._createAbscissaAndOrdinateAxisValues(abscissaVariable, ordinateVariable, valuesForSeries)

                series = _Series(i, seriesGroupingValue, chunkGroupingValue,
                                 abscissaValues, ordinateValues, shallPrintUncertainties)

                allSeries.append(series)

            return allSeries

        allSeries = []
        for chunkValue, chunkGroupingValue in values.items():
            for seriesValue, valuesForSeries in chunkGroupingValue.items():
                i = len(allSeries) + 1
                seriesGroupingValue = _GroupingValue(seriesVariable, seriesValue)
                chunkGroupingValue = _GroupingValue(chunkVariable, chunkValue)

                abscissaValues, ordinateValues = \
                    cls._createAbscissaAndOrdinateAxisValues(abscissaVariable, ordinateVariable, valuesForSeries)

                series = _Series(i, seriesGroupingValue, chunkGroupingValue,
                                 abscissaValues, ordinateValues, shallPrintUncertainties)

                allSeries.append(series)

        return allSeries

    @classmethod
    def _createAbscissaAndOrdinateAxisValues(cls, abscissaVariable, ordinateVariable, valuesForSeries):
        xs, xerrors, ys, yerrors = _getXAndYValuesAndErrorsOrderedByXValues(valuesForSeries)
        xAxisValues = cls._createAxisValues(abscissaVariable, xs, xerrors)
        yAxisValues = cls._createAxisValues(ordinateVariable, ys, yerrors)
        return xAxisValues, yAxisValues

    @staticmethod
    def _createAxisValues(variableName, means, errors):
        xAxisValues = _AxisValues(variableName,
                                  mins=means - errors[:, 0],
                                  means=means,
                                  maxs=means + errors[:, 1])
        return xAxisValues

    def __post_init__(self):
        if self.abscissa.length != self.ordinate.length:
            raise ValueError("`abscissaValues` and `ordinateValues` must be the same length.")
        self.length = self.abscissa.length

        if self.series and self.index is None:
            raise ValueError("If you specify a `series` you also need to provide an `index`.")

        if self.chunk and not self.series:
            raise ValueError("If you specify a `chunk` you must also specify a `series` .")

        self._indexedAbscissaName = f"{self.abscissa.name}_{self.index}"

        self._signs = ["-", "=", "+"] if self.shallPrintUncertainties else [""]

    def getAbscissaHeader(self):
        parts = self._getAbscissaHeaderParts()
        return "\t".join(parts)

    def getOrdinateHeader(self):
        parts = self._getOrdinateHeaderParts()
        return "\t".join(parts)

    def _getAbscissaHeaderParts(self):
        if not self.series:
            return [f"{self.abscissa.name}{sign}" for sign in self._signs]

        return [f"{self._indexedAbscissaName}{sign}" for sign in self._signs]

    def _getOrdinateHeaderParts(self):
        if not self.series:
            return [f"{self.ordinate.name}{sign}({self.abscissa.name})" for sign in self._signs]

        if not self.chunk:
            return [f"{self.ordinate.name}{sign}({self._indexedAbscissaName},{self.series.value})"
                    for sign in self._signs]

        return [f"{self.ordinate.name}{sign}({self._indexedAbscissaName},{self.series.value},{self.chunk.value})"
                for sign in self._signs]


@_dc.dataclass()
class _GroupingValue:
    name: str
    value: float


@_dc.dataclass()
class _AxisValues:
    name: str
    mins: _tp.Sequence[float]
    means: _tp.Sequence[float]
    maxs: _tp.Sequence[float]

    def __post_init__(self):
        self._ensureAlLengthsEqualOrValueError()

        self.length = len(self.means)

    def _ensureAlLengthsEqualOrValueError(self):
        lens = {len(self.mins), len(self.means), len(self.maxs)}

        if len(lens) != 1:
            raise ValueError("`mins`, `means` and `maxs` must all be same length.")


def _getColumnHeadersLegend(abscissaVariable, ordinateVariable, seriesVariable, chunkVariable):
    if not seriesVariable:
        return f"{ordinateVariable}={ordinateVariable}({abscissaVariable})"

    if not chunkVariable:
        return f"{ordinateVariable}={ordinateVariable}({abscissaVariable}_j, {seriesVariable})"

    return f"{ordinateVariable}={ordinateVariable}({abscissaVariable}_j, {seriesVariable}, {chunkVariable})"


def _formatUncertainValue(uMin, u, uMax, shallPlotUncertainties):
    if not shallPlotUncertainties:
        return _formatValue(u)

    formattedValues = [_formatValue(v) for v in [uMin, u, uMax]]

    return "\t".join(formattedValues)


def _formatValue(u):
    if isinstance(u, str):
        return u

    return f"{u:8.4f}"
