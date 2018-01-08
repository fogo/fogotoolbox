import asyncio
import os
import socket

import pytest
from fogotoolbox.unix.network import IP_SCTP, find_sctp_assocs


def test_find_sctp_assocs(loop):
    class State:
        def __init__(self):
            self.ep_ready = asyncio.Event()
            self.ep_done = asyncio.Event()
            self.ep_port = None
            self.assoc_port = None
            self.assoc_fd = None
            self.assocs = {}

    state = State()
    loop.run_until_complete(
        asyncio.wait([create_ep(state, loop), create_assoc(state, loop)]))

    assert state.assoc_port is not None
    assert state.assocs[state.assoc_port] == state.assoc_fd


async def create_ep(state, loop):
    ep = socket.socket(socket.AF_INET, socket.SOCK_STREAM, IP_SCTP)
    ep.setblocking(0)
    ep.bind(("127.0.0.1", 0))
    ep.listen(1)
    _, state.ep_port = ep.getsockname()

    state.ep_ready.set()
    _, (_, state.assoc_port) = await loop.sock_accept(ep)

    state.assocs.update(find_sctp_assocs(os.getpid()))

    state.ep_done.set()


async def create_assoc(state, loop):
    await state.ep_ready.wait()
    assoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM, IP_SCTP)
    state.assoc_fd = assoc.fileno()
    assert state.ep_port is not None
    assoc.connect(("127.0.0.1", state.ep_port))
    await state.ep_done.wait()


@pytest.fixture
def loop():
    loop_ = asyncio.get_event_loop()
    loop_.set_debug(True)
    return loop_
