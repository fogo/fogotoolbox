from typing import Dict


# Extracted from:
# /usr/include/netinet/sctp.h
# IPPROTO_SCTP    132
IP_SCTP = 132


def find_sctp_assocs(pid: int) -> Dict[int, int]:
    """
    Find SCTP associations associated with a process.

    :return: A dictionary in the format {assoc port: assoc fd}
    """
    import re
    import subprocess

    # -n: inhibits the conversion of network numbers to host names for
    # network  files
    # -p: only open files of pid
    lsof = subprocess.check_output(
        "lsof -np {pid}| grep SCTP".format(pid=pid),
        shell=True,
        stderr=subprocess.DEVNULL,
    )
    lsof = lsof.decode("utf8")

    assocs = {}  # type: Dict[int, int]
    for line in lsof.splitlines():
        # regex breakdown:
        # \w+: command
        # \s+: separator
        # (\d+): pid
        # \s+: separator
        # \w+: user
        # \s+: separator
        # (\d+)u: fd
        # \s+: separator
        # sock: type
        # \s+: separator
        # \d+: device
        # \s+: separator
        # 0t0: size/offset
        # \s+: separator
        # SCTP ASSOC:(.+): node name
        #
        # A line example:
        # foobar 1602 root  630u     sock  42922      0t0    SCTP ASSOC: ffff880248123000,1 10.3.0.39[3594]<->*10.3.0.39[3565]  # noqa: E501
        assoc_match = re.match(
            r"\w+\s+(\d+)\s+\w+\s+(\d+)u\s+sock\s+\d+\s+0t0\s+SCTP ASSOC:(.+)",
            line)
        if not assoc_match:
            continue

        pid_found = int(assoc_match.group(1))
        assert pid_found == pid, \
            "lsof should have filtered only pid={} but " \
            "somehow found pid={} too".format(pid, pid_found)

        conn = assoc_match.group(3)
        port_match = re.match(r".+\[(\d+)\]<->.+", conn)
        assert port_match is not None, \
            "port regex unable to match {}".format(conn)
        assocs[int(port_match.group(1))] = int(assoc_match.group(2))

    return assocs
