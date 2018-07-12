import subprocess

import pytest

from fogotoolbox.unix.cc import is_pic


@pytest.mark.parametrize(
    "input_mode",
    ["path", "str"]
)
@pytest.mark.parametrize(
    "fpic",
    ["yes", "no"]
)
def test_is_pic(shared_datadir, input_mode, fpic):
    c_file = shared_datadir / "cc" / "foo.c"
    o_file = shared_datadir / "cc" / "foo.o"
    expected_pic = fpic == "yes"
    fpic = "-fPIC" if expected_pic else ""
    # TODO: test w/ clang/x86/x64
    subprocess.check_call(f"gcc -c -O0 {fpic} {c_file} -o {o_file}", shell=True)

    path = o_file if input_mode == "path" else str(o_file)
    assert is_pic(path) == expected_pic
