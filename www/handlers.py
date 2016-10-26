#!/usr/bin/env python3
# -*- coding: utf-8 *-*

import asyncio
import aiohttp
from coroweb import get, post
from models import User

__author__= 'Aiss86'

'url handler'

'''
async def handle_url_xxx(requeset):
    url_param = request.match_info['key']
    query_params = parse_qs(request.query_string)
    text = render('template', data)
    return web.Response(text.encode('utf-8'))
'''

@get('/')
async def index(request):
    users = await User.findAll()
    return {
        '__template': 'test.html',
        'users': users
    }
