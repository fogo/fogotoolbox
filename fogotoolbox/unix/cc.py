import re
import subprocess
import sys
from typing import Union


def is_pic(filename: Union[str, "Path"]) -> bool:
    # TODO: organize/read refs
    # https://codywu2010.wordpress.com/2014/11/29/about-elf-pie-pic-and-else/
    # https://stackoverflow.com/questions/1340402/how-can-i-tell-with-something-like-objdump-if-an-object-file-has-been-built-wi
    # http://www.openbsd.org/papers/nycbsdcon08-pie/mgp00001.html
    relocs = subprocess.check_output(f"readelf --relocs {filename}", shell=True)
    relocs = relocs.decode(sys.stdout.encoding)
    return re.search(r"(GOT|PLT|JU?MP_SLOT)", relocs) is not None
