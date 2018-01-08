import subprocess

from fogotoolbox.unix.gdb import instrument_gdb


def test_gdb(shared_datadir):
    process = subprocess.Popen(str(shared_datadir / "foobar"))
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
