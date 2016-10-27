#!/usr/bin/env python3
# -*- coding: utf-8 *-*

import asyncio
import aiohttp
import time
from coroweb import get, post
from models import User, Blog

__author__= 'Aiss86'

'url handler'

'''
async def handle_url_xxx(requeset):
    url_param = request.match_info['key']
    query_params = parse_qs(request.query_string)
    text = render('template', data)
    return web.Response(text.encode('utf-8'))
'''
'''
@get('/')
async def index(request):
    users = await User.findAll()
    return {
        '__template__': 'test.html',
        'users': users
    }
'''
@get('/')
def index(request):
    summary = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
    blogs = [
        Blog(id='1', name='Test Blog', summary=summary, created_at=time.time()-120),
        Blog(id='2', name='Something New', summary=summary, created_at=time.time()-3600),
        Blog(id='3', name='Learn Swift', summary=summary, created_at=time.time()-7200)
    ]
    return {
        '__template__': 'blogs.html',
        'blogs': blogs
    }