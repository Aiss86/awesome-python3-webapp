#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import logging
import asyncio
from aiohttp import web

__author__ = 'Aiss86'

logging.basicConfig(level=logging.INFO)


def index(request):
    return web.Response(body=b'<h1>Awesome</h1>',
                             content_type='text/html', charset='utf-8')


async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', index)
    srv = await loop.create_server(app.make_handler(), '127.0.0.1', 9000)
    logging.info('server started at http://127.0.0.1:9000...')
    return srv


loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
