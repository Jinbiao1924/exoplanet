#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function

import re
import sys
import glob

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor, CellExecutionError

if len(sys.argv) >= 2:
    pattern = sys.argv[1]
else:
    pattern = "_static/notebooks/*.ipynb"


errors = []

for filename in glob.glob(pattern):
    with open(filename) as f:
        notebook = nbformat.read(f, as_version=4)

    ep = ExecutePreprocessor(timeout=-1)

    print("running: {0}".format(filename))
    try:
        ep.preprocess(notebook, {"metadata": {"path": "_static/notebooks/"}})
    except CellExecutionError as e:
        msg = "error while running: {0}\n\n".format(filename)
        msg += e.traceback
        print(msg)
        errors.append(msg)
    finally:
        with open(filename, mode="wt") as f:
            nbformat.write(notebook, f)

txt = "\n\n".join(errors)
ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
txt = ansi_escape.sub("", txt)

with open("notebook_errors.log", "wb") as f:
    f.write(txt.encode("utf-8"))
