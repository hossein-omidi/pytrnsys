#!/usr/bin/python3.9

# Run from top-level directory

import pathlib as pl
import shutil as sh
import subprocess as sp
import argparse as ap
import time
import sys


def main():
    parser = ap.ArgumentParser()

    parser.add_argument(
        "-k",
        "--keep-results",
        help="Don't clean test results",
        action="store_true",
        dest="shallKeepResults",
    )

    parser.add_argument(
        "-s",
        "--static-checks",
        help="Also perform static checks",
        action="store_true",
        dest="shallPerformStaticChecks",
    )
    parser.add_argument(
        "-l", "--lint", help="Perform linting", action="store_true", dest="shallLint"
    )
    parser.add_argument(
        "-t",
        "--type",
        help="Perform type checking",
        action="store_true",
        dest="shallTypeCheck",
    )
    parser.add_argument(
        "-u",
        "--unit",
        help="Perform unit tests",
        action="store_true",
        dest="shallRunTests",
    )
    parser.add_argument(
        "-d",
        "--diagram",
        help="Create package and class diagrams",
        action="store_true",
        dest="shallCreateDiagrams",
    )
    parser.add_argument(
        "-a",
        "--all",
        help="Perform all checks",
        action="store_true",
        dest="shallRunAll",
    )
    arguments = parser.parse_args()

    testResultsDirPath = pl.Path("test-results")
    if testResultsDirPath.exists() and not testResultsDirPath.is_dir():
        print("ERROR: `test-results` exists but is not a directory", file=sys.stderr)
        sys.exit(2)

    _prepareTestResultsDirectory(testResultsDirPath, arguments.shallKeepResults)

    if (
        arguments.shallRunAll
        or arguments.shallPerformStaticChecks
        or arguments.shallTypeCheck
    ):
        cmd = "mypy pytrnsys tests dev-tools"
        sp.run(cmd.split(), check=True)

    if (
        arguments.shallRunAll
        or arguments.shallPerformStaticChecks
        or arguments.shallLint
    ):
        cmd = "pylint pytrnsys tests dev-tools"
        sp.run(cmd.split(), check=True)

    if arguments.shallRunAll or arguments.shallCreateDiagrams:
        cmd = "pyreverse -k -o pdf -p pytrnsys -d test-results pytrnsys"
        sp.run(cmd.split(), check=True)

    if (
        arguments.shallRunAll
        or arguments.shallRunTests
        or not (
            arguments.shallPerformStaticChecks
            or arguments.shallTypeCheck
            or arguments.shallLint
            or arguments.shallCreateDiagrams
        )
    ):
        args = [
            "pytest",
            "--cov=pytrnsys",
            f"--cov-report=html:{testResultsDirPath / 'coverage'}",
            "--cov-report=term",
            f"--html={testResultsDirPath / 'report' / 'report.html'}",
            "-m",
            "not manual",
            "tests",
        ]
        sp.run(args, check=True)


def _prepareTestResultsDirectory(testResultsDirPath: pl.Path, shallKeepResults: bool) -> None:
    if not shallKeepResults and testResultsDirPath.is_dir():
        sh.rmtree(testResultsDirPath)

    # Sometimes we need to give Windows a bit of time so that it can realize that
    # the directory is gone and it allows us to create it again.
    time.sleep(1)

    if not testResultsDirPath.is_dir():
        testResultsDirPath.mkdir()


if __name__ == "__main__":
    main()
