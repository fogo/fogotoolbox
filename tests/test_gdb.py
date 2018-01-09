import subprocess

import pytest

from fogotoolbox.unix.gdb import instrument_gdb


def test_gdb(shared_datadir):
    process = subprocess.Popen(
        str(shared_datadir / "foobar"), stdout=subprocess.DEVNULL)
    try:
        stdout_path = shared_datadir / "stdout.txt"
        with open(stdout_path, "w") as stdout:
            instrument_gdb(
                process.pid,
                commands=[
                    "shell echo gdb printed this",
                ],
                stdout=stdout,
            )
        with open(stdout_path, "r") as stdout:
            assert "gdb printed this" in stdout.read()
    finally:
        process.terminate()
        process.wait()


def test_gdb_failure_not_found(mocker):
    mocker.patch.object(subprocess, "call", return_value=1)
    with pytest.raises(FileNotFoundError) as e:
        instrument_gdb(
            42,
            commands=[
                "not going to be executed anyway",
            ],
        )

    assert str(e.value) == "gdb not found"
