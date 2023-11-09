#!/usr/bin/env python3
# SPDX-FileCopyrightText: Christian Amsüss and the aiocoap contributors
#
# SPDX-License-Identifier: MIT

import sys
import asyncio
import logging
import argparse
from pathlib import Path

import aiocoap
import aiocoap.oscore as oscore
from aiocoap.oscore_sitewrapper import OscoreSiteWrapper
import aiocoap.error as error
from aiocoap.util.cli import AsyncCLIDaemon
import aiocoap.resource as resource
from aiocoap.credentials import CredentialsMap
from aiocoap.cli.common import add_server_arguments, server_context_from_arguments

from aiocoap.transports.oscore import OSCOREAddress

# In some nested combinations of unittest and coverage, the usually
# provided-by-default inclusion of local files does not work. Ensuring the
# local plugtest_common *can* be included.
import os.path
sys.path.append(os.path.dirname(__file__))
from common import *

class PleaseUseOscore(error.ConstructionRenderableError):
    code = aiocoap.UNAUTHORIZED
    message = "This is an OSCORE plugtest, please use option %d"%aiocoap.numbers.optionnumbers.OptionNumber.OBJECT_SECURITY

def additional_verify_request_options(reference, request):
    if request.opt.echo is not None:
        # Silently accepting Echo as that's an artefact of B.1.2 recovery
        reference.opt.echo = request.opt.echo
    additional_verify("Request options as expected", reference.opt, request.opt)

class PlugtestResource(resource.Resource):
    options = {}
    expected_options = {}

    async def render_get(self, request):
        reference = aiocoap.Message(**self.expected_options)
        if request.opt.observe is not None and 'observe' not in self.expected_options:
            # workaround for test 4 hitting on Hello1
            reference.opt.observe = request.opt.observe
        additional_verify_request_options(reference, request)

        return aiocoap.Message(payload=self.message, **self.options)

class Hello(PlugtestResource):
    options = {'content_format': 0}

    expected_options = {} # Uri-Path is stripped by the site
    with open("stix_data.json") as f:
        message = f.read()

    message= b'\xa7\x02\x15\x03c2.1\x08x.identity--55f6ea5e-2c60-40e5-964f-47a8950d210f\x10x\x182021-03-12T09:33:28.000Z\x0fx\x182021-03-12T09:33:28.000Z\x0eeCIRCL\x18\x92\x04'
Hello1 = Hello # same, just registered with the site for protected access


class Observe(PlugtestResource, aiocoap.interfaces.ObservableResource):
    expected_options = {'observe': 0}
    options = {'content_format': 0}
    data_list = []
    with open("../reference_testing/data/botvrij/tinystix_data/02a470d8-493e-41d9-8367-622460dddbe8_first_line.txt", "rb") as file:
        while True:
            # Read a line (up to the delimiter) and break if the end of file is reached
            line = file.readline()
            if not line:
                break
            # Append the byte-string to the list
            data_list.append(line.strip())
    message = b"no data" if not data_list else data_list[0]

    async def add_observation(self, request, serverobservation):
        async def keep_entertained():

            for data in self.data_list[1:]:
                await asyncio.sleep(0.01)
                serverobservation.trigger(aiocoap.Message(
                mtype=aiocoap.CON, code=aiocoap.CONTENT,
                payload=data, content_format=0,
                ))
            await asyncio.sleep(0.01)
            serverobservation.trigger(aiocoap.Message(
                mtype=aiocoap.CON, code=aiocoap.INTERNAL_SERVER_ERROR,
                payload=b"Terminate Observe", content_format=0,
                ))
        t = asyncio.create_task(keep_entertained())
        serverobservation.accept(t.cancel)

class DeleteResource(resource.Resource):
    async def render_delete(self, request):
        additional_verify_request_options(aiocoap.Message(), request)
        return aiocoap.Message(code=aiocoap.DELETED)

class BlockResource(PlugtestResource):
    expected_options = {}
    options = {'content_format': 0}

    message = "This is a large resource\n" + "0123456789" * 101

class InnerBlockMixin:
    # this might become general enough that it could replace response blockwise
    # handler some day -- right now, i'm only doing the absolute minimum
    # necessary to satisfy the use case

    inner_default_szx = aiocoap.MAX_REGULAR_BLOCK_SIZE_EXP

    async def render(self, request):
        response = await super().render(request)

        if request.opt.block2 is None:
            szx = self.inner_default_szx
            blockno = 0
        else:
            szx = request.opt.block2.size_exponent
            blockno = request.opt.block2.block_number

        return response._extract_block(blockno, szx)

class InnerBlockResource(InnerBlockMixin, BlockResource):
    pass

class SeqnoManager(resource.ObservableResource):
    def __init__(self, contextmap):
        super().__init__()
        self.contextmap = contextmap

        for c in self.contextmap.values():
            c.notification_hooks.append(self.updated_state)

    async def render_get(self, request):
        text = ""
        for name in ('b', 'd'):
            the_context = self.contextmap[':' + name]

            # this direct access is technically outside the interface for a
            # SecurityContext, but then again, there isn't one yet
            text += """In context %s, next seqno is %d (persisted up to %d)\n""" % (name.upper(), the_context.sender_sequence_number, the_context.sequence_number_persisted)
            if the_context.recipient_replay_window.is_initialized():
                index = the_context.recipient_replay_window._index
                bitfield = the_context.recipient_replay_window._bitfield
                # Useless for the internal representation, but much more readable
                while bitfield & 1:
                    bitfield >>= 1
                    index += 1
                print(index, bitfield)
                bitfield_values = [i + index for (i, v) in enumerate(bin(bitfield)[2:][::-1]) if v == '1']
                text += """I've seen all sequence numbers lower than %d%s.""" % (
                        index,
                        ", and also %s" % bitfield_values if bitfield else ""
                        )
            else:
                text += "The replay window is uninitialized"
            text += "\n"
        return aiocoap.Message(payload=text.encode('utf-8'), content_format=0)

    async def render_put(self, request):
        try:
            number = int(request.payload.decode('utf8'))
        except (ValueError, UnicodeDecodeError):
            raise aiocoap.error.BadRequest("Only numeric values are accepted.")

        raise NotImplementedError

class Site(resource.Site):
    def __init__(self, server_credentials):
        super().__init__()

        self.add_resource(['.well-known', 'core'], resource.WKCResource(self.get_resources_as_linkheader))
        self.add_resource(['oscore', 'hello', 'coap'], Hello())
        self.add_resource(['oscore', 'observe1'], Observe())
        self.add_resource(['sequence-numbers'], SeqnoManager(server_credentials))

class ServerProgram(AsyncCLIDaemon):
    async def start(self):
        p = argparse.ArgumentParser()
        p.add_argument("contextdir", help="Directory name where to persist sequence numbers", type=Path)
        p.add_argument('--verbose', help="Increase log level", action='store_true')
        p.add_argument('--state-was-lost', help="Lose memory of the replay window, forcing B.1.2 recovery", action='store_true')
        add_server_arguments(p)
        opts = p.parse_args()

        if opts.verbose:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.WARNING)


        server_credentials = CredentialsMap()
        server_credentials[':b'] = get_security_context('b', opts.contextdir / "b", opts.state_was_lost)
        server_credentials[':d'] = get_security_context('d', opts.contextdir / "d", opts.state_was_lost)

        site = Site(server_credentials)
        site = OscoreSiteWrapper(site, server_credentials)

        self.context = await server_context_from_arguments(site, opts)

        print("Test server ready.")
        sys.stdout.flush() # the unit tests might wait abundantly long for this otherwise

    async def shutdown(self):
        await self.context.shutdown()

if __name__ == "__main__":
    ServerProgram.sync_main()
