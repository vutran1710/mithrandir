from subprocess import check_call


def lint() -> None:
    check_call(["radon", "mi", "mithrandir/"])
    check_call(["black", "mithrandir/"])
    check_call(["flake8", "mithrandir/"])
    check_call(["pylint", "mithrandir/", "--rcfile=setup.cfg"])
    check_call(["autopep8", "mithrandir/*.py"])


def test() -> None:
    check_call(
        [
            "pytest",
            "tests",
            "--maxfail=1",
            "--verbose",
            "-s",
            "--cov-report",
            "term-missing",
            "--disable-warnings",
            "--cov=.",
        ]
    )


def test_box() -> None:
    check_call(
        [
            "pytest",
            "tests/test_box.py",
            "--maxfail=1",
            "--verbose",
            "-s",
        ]
    )
