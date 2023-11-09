#!/usr/bin/env python3
# SPDX-FileCopyrightText: Christian Amsüss and the aiocoap contributors
#
# SPDX-License-Identifier: MIT

import argparse
import asyncio
import logging
import signal
import functools
from pathlib import Path
import sys

from aiocoap import *
from aiocoap import error
from aiocoap import interfaces
from aiocoap import credentials

# In some nested combinations of unittest and coverage, the usually
# provided-by-default inclusion of local files does not work. Ensuring the
# local common *can* be included.
import os.path
sys.path.append(os.path.dirname(__file__))
from common import *


class PlugtestClientProgram:
    async def run(self):
        p = argparse.ArgumentParser(description="Client for the OSCORE plug test.")
        p.add_argument("host", help="Hostname of the server")
        p.add_argument("contextdir", help="Directory name where to persist sequence numbers", type=Path)
        p.add_argument("testno", nargs="?", type=int, help="Test number to run (integer part); leave out for interactive mode")
        p.add_argument("--verbose", help="Show aiocoap debug messages", action='store_true')
        opts = p.parse_args()

        self.host = opts.host

        # this also needs to be called explicitly as only the
        # 'logging.warning()'-style functions will call it; creating a
        # sub-logger and logging from there makes the whole logging system not
        # emit the 'WARNING' prefixes that set apart log messages from regular
        # prints and also help the test suite catch warnings and errors
        if opts.verbose:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.WARNING)

        security_context_a = get_security_context('a', opts.contextdir / "a")
        security_context_c = get_security_context('c', opts.contextdir / "c")

        self.ctx = await Context.create_client_context()
        self.ctx.client_credentials[":ab"] = security_context_a
        self.ctx.client_credentials[":cd"] = security_context_c

        try:
            await self.run_test()
        except error.Error as e:
            print("Test failed with an exception:", e)

    ctx = None

    async def run_with_shutdown(self):
        # Having SIGTERM cause a more graceful shutdown (even if it's not
        # asynchronously awaiting the shutdown, which would be impractical
        # since we're likely inside some unintended timeout already) allow for
        # output buffers to be flushed when the unit test program instrumenting
        # it terminates it.
        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGTERM, loop.close)

        try:
            await self.run()
        finally:
            if self.ctx is not None:
                await self.ctx.shutdown()

    def use_context(self, which):
        if which is None:
            self.ctx.client_credentials.pop("coap://%s/*" % self.host, None)
        else:
            self.ctx.client_credentials["coap://%s/*" % self.host] = ":" + which

    async def run_test(self):
        try:
            await self.test_plain()
        except oscore.NotAProtectedMessage as e:
            print("Response carried no Object-Security option, but was: %s %s"%(e.plain_message, e.plain_message.payload))
            raise

    async def test_plain(self):
        # request = Message(code=GET, uri='coap://' + self.host + '/oscore/observe2')

        self.use_context("ab")

        # response = await self.ctx.request(request).response

        # print("Response:", response)
        # additional_verify("Responde had correct code", response.code, CONTENT)
        # additional_verify("Responde had correct payload", response.payload, b"Hello World!")
        # additional_verify("Options as expected", response.opt, Message(content_format=0).opt)


        #self.use_context(None)

        request = Message(code=GET, uri='coap://' + self.host + '/oscore/observe1', observe=0)

        request = self.ctx.request(request)

        unprotected_response = await request.response

        #print("Unprotected response:", unprotected_response)
        # additional_verify("Code as expected", unprotected_response.code, CONTENT)
        # additional_verify("Observe option present", unprotected_response.opt.observe is not None, True)

        payloads = [unprotected_response.payload]
        i = 0
        async for o in request.observation:
            i+=1
            payloads.append(o.payload)
            print("Verify: Received message", o, o.payload)
            print(i)
            
        # expected_payloads = [b'one', b'two']
        # expected_payloads.append(b'Terminate Observe')
        # additional_verify("Server gave the correct responses", payloads, b'one')


        print("\n\n", payloads, "\n\n")

if __name__ == "__main__":
    asyncio.run(PlugtestClientProgram().run_with_shutdown())
