import subprocess
from typing import List


def instrument_gdb(
    pid: int,
    commands: List[str],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
):
    """
    Attaches to gdb to a process and executes a list of commands.

    This is useful to interfere with running processes for testing purposes.
    For instance, you can use this to close a socket in a process to simulate
    a connection loss.

    :param pid: A pid.
    :param commands: A list of commands. Every item in list is considered a
        command line and it is automatically appended a line separator by
        underlying code. It also takes care of using correct terminal
        encoding. Once all commands are done it also automatically ends
        gdb session, so a command to end session is unnecessary.
    :param stdout: Refer to subprocess.Popen.
    :param stderr: Refer to subprocess.Popen.
    """
    if not has_gdb():
        raise FileNotFoundError("gdb not found")

    gdb = subprocess.Popen(
        "gdb -p {}".format(pid),
        shell=True,
        stdin=subprocess.PIPE,
        stdout=stdout,
        stderr=stderr)
    for command in commands:
        command = "{}\n".format(command).encode("utf8")
        gdb.stdin.write(command)
        gdb.stdin.flush()

    gdb.stdin.write(b"quit\n")
    gdb.stdin.flush()
    gdb.wait(timeout=5)


def has_gdb() -> bool:
    """
    Is gdb available on user path?
    """
    return subprocess.call("gdb --version > /dev/null", shell=True) == 0
