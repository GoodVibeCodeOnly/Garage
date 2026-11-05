"""Shared test plumbing. You never need to edit this file.

Every lesson's tests ask for a fixture called `ex`. That fixture is the module
you are working on: lessons/NN_name/exercises.py. When the checker is run in
"solutions" mode it loads solutions/NN_name/exercises.py instead, so the same
tests verify both your work and the model answers.
"""
import importlib.util
import os
import pathlib

import pytest

COURSE = pathlib.Path(__file__).parent


def _load(path: pathlib.Path):
    name = "course_" + path.parent.name + "_" + path.parent.parent.name
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def lesson_dir(request) -> pathlib.Path:
    """The lesson folder (where data/ lives), whichever version is being tested."""
    return pathlib.Path(request.path).parent


@pytest.fixture
def data_dir(lesson_dir) -> pathlib.Path:
    return lesson_dir / "data"


@pytest.fixture
def ex(lesson_dir):
    if os.environ.get("COURSE_SOLUTIONS") == "1":
        path = COURSE / "solutions" / lesson_dir.name / "exercises.py"
    else:
        path = lesson_dir / "exercises.py"
    return _load(path)
