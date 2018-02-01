import atexit
import os
import pwd
import re
import subprocess
from contextlib import contextmanager


def pgrep(pattern: str) -> int:
    """
    A simple, pgrep-like python utility. Finds pid of first process
    whose command matches pattern.
    """
    for root, dirs, files in os.walk("/proc/"):
        for pid in dirs:
            # only interested in process folders
            if not pid.isnumeric():
                continue

            cmdline_path = os.path.join(root, pid, "cmdline")
            if not os.path.isfile(cmdline_path):
                continue
            cmdline = open(cmdline_path, "r").read()
            if re.search(pattern, cmdline):
                return int(pid)

    raise LookupError("Unable to find pid for pattern '{}'".format(pattern))


def is_superuser() -> bool:
    """
    Is current user the superuser?
    """
    pwuid = pwd.getpwuid(os.getuid())
    return pwuid.pw_uid == 0


_temp_cfg = set()


@contextmanager
def temp_mount(path: str, name: str):
    """
    Stacks a temporary file system (tmpfs) on given path.

    Note that tmpfs is mounted on memory and has a limited size, so be aware
    of how much files you store in it. For more details refer to
    [its man page](http://man7.org/linux/man-pages/man5/tmpfs.5.html).

    This can be especially useful when testing programs that have hardcoded/
    non-configurable paths and you want to temporarily alter contents to
    perform a specific test (for instance, changing a configuration file
    before starting a service).

    :param path: Where tmpfs is going to be mounted.
    :param name: Name of tmpfs.
    """
    global _temp_cfg

    if not is_superuser():
        raise PermissionError("Requires superuser")

    abs_path = os.path.abspath(path)
    if not os.path.isdir(abs_path):
        raise NotADirectoryError("{} is not a directory".format(abs_path))

    # stack a temporary file system on given path
    subprocess.check_call(
        "mount -t tmpfs {name} {abs_path}".format(
            name=name, abs_path=abs_path),
        shell=True)
    _temp_cfg.add(abs_path)

    yield

    _umount_tmpfs(abs_path)


def _umount_tmpfs(path):
    try:
        _temp_cfg.remove(path)
        subprocess.check_output("umount {}".format(path), shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        # if not mounted anymore, no reason to fail
        if not re.search(r"umount: .+: not mounted", e.output.decode("utf-8")):
            raise


def _always_umount_temp_cfg():
    if True:  # pragma: no cover
        paths = list(_temp_cfg)
        while paths:
            path = paths[0]
            _umount_tmpfs(path)


atexit.register(_always_umount_temp_cfg)
