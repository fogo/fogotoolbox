import os
import pwd
import subprocess
import tempfile

import pytest

from fogotoolbox.unix.system import pgrep, temp_mount, is_superuser


def test_find_pid_success(shared_datadir):
    process = subprocess.Popen(str(shared_datadir / "foobar"))
    try:
        assert pgrep("foobar") == process.pid
    finally:
        process.terminate()
        process.wait()


def test_find_pid_failure():
    with pytest.raises(LookupError) as e:
        pgrep("&&&")
    assert str(e.value) == "Unable to find pid for pattern '&&&'"


def test_temp_mount(shared_datadir):
    if not is_superuser():
        pytest.xfail("can only run this test as superuser")

    tmp = tempfile.mkdtemp(dir=shared_datadir)

    path = os.path.join(tmp, "test")
    with open(path, "w") as f:
        f.write("hello world")
    assert os.path.isfile(path)

    # tmpfs starts empty, test file should no longer exist
    with temp_mount(shared_datadir, "testtempmount"):
        assert not os.path.isfile(path)

    # tmpfs umounted, test file should be back
    assert os.path.isfile(path)

    # make sure tmpfs was umounted on tear down
    tmpfs = subprocess.check_output("mount | grep tmpfs", shell=True)
    tmpfs = tmpfs.decode("utf8")
    assert "testtempmount" not in tmpfs


def test_temp_mount_failure_not_superuser(mocker):
    def fake(_):
        class Fake:
            def __init__(self):
                self.pw_uid = 1000

        return Fake()

    mocker.patch.object(pwd, "getpwuid", side_effect=fake, autospec=True)
    with pytest.raises(PermissionError) as e:
        with temp_mount("doesnt_matter", "testtempmount"):
            assert pwd.getpwuid.called
    assert str(e.value) == "Requires superuser"


def test_temp_mount_failure_not_dir(mocker, shared_datadir):
    # force always to be superuser, as it will fail because of
    # directory anyway
    def fake(_):
        class Fake:
            def __init__(self):
                self.pw_uid = 0

        return Fake()

    mocker.patch.object(pwd, "getpwuid", side_effect=fake, autospec=True)
    with pytest.raises(NotADirectoryError) as e:
        invalid_dir = shared_datadir / "&&&"
        with temp_mount(invalid_dir, "testtempmount"):
            assert pwd.getpwuid.called
    assert str(e.value) == "{} is not a directory".format(invalid_dir)
