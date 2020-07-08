import setuptools
from glob import glob
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

examples_data_files = []
directories = glob('pytrnsys-examples/**/', recursive=True)
directories.extend(glob('ddck/**/', recursive=True))
print(directories)
for directory in directories:
    files = glob(directory+'*.*')
    examples_data_files.append((os.path.join('pytrnsys-files',os.path.dirname(directory)), files))

setuptools.setup(
    name="pytrnsys", # Replace with your own username
    version="0.1",
    author="Dani Carbonell, Mattia Battaglia, Jeremias Schmidli",
    author_email="dani.carbonell@spf.ch",
    description="pytrnsys simulation framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data={'pytrnsys_examples': ['./*.*','./**/*.*','./**/**/*.*'],
                  'pytrnsys_ddck': ['./*.*','./**/*.*','./**/**/*.*','./**/**/**/*.*','./**/**/**/**/*.*','./**/**/**/**/**/*.*'],
                  'pytrnsys': ['./plot/stylesheets/*.*','./report/latex_doc/*.*']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Windows",
    ],
	entry_points="""
    [console_scripts]
    pytrnsys-run = pytrnsys.rsim.runParallelTrnsys:run
    pytrnsys-process = pytrnsys.psim.processParallelTrnsys:process
    pytrnsys-load = pytrnsys.utils.loadExamplesAndDdcks:load
    """,
    python_requires='>=3.5',
)