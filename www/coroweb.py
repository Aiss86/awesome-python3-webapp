#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import asyncio
import os
import inspect
import functools
import logging
from apis import APIError
from aiohttp import web
from urllib import parse


__author__ = "Aiss86"


def get(path):
    '''
    Define decorator @get('/path')
    '''
    def decorator(func):
        @functools.wraps(func)
        def warpper(*args, **kw):
            return func(*args, **kw)
        warpper.__method__ = 'GET'
        warpper.__route__ = path
        return warpper
    return decorator


def post(path):
    '''
    Define decorator @post('/path')
    '''
    def decorator(func):
        @functools.wraps(func)
        def warpper(*args, **kw):
            return func(*args, **kw)
        warpper.__method__ = 'POST'
        warpper.__route__ = path
        return warpper
    return decorator


def get_requried_kw_args(fn):
    '''
    获取请求的关键字名字
    '''
    args = []
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY and param.default == inspect.Parameter.empty:
            args.append(name)
    return tuple(args)


def get_named_kw_args(fn):
    '''
    获取函数的关键字名字
    '''
    args = []
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            args.append(name)
    return tuple(args)


def has_named_kw_args(fn):
    '''
    函数是否仅关键字参数
    '''
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            logging.info(' function(%s) has only keyword!!!' % fn.__name__)
            return True
    logging.info(' function(%s) has not only keyword!!!' % fn.__name__)


def has_var_kw_arg(fn):
    '''
    函数是否为任意关键字参数？
    '''
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            logging.info(' function(%s) has var keywords!!!' % fn.__name__)
            return True
    logging.info(' function(%s) has not keyword!!!' % fn.__name__)


def has_request_arg(fn):
    '''
    函数有request参数？
    '''
    sig = inspect.signature(fn)
    params = sig.parameters
    logging.info("function(%s)'s sig:%s params:%s" % (fn.__name__, sig, list(params)))
    found = False
    for name, param in params.items():
        logging.info('  name:%s param.kind(%s:%s)' % (name, param, param.kind))
        if name == 'request':
            found = True
            logging.info(' function(%s) has request parameter!!!' % fn.__name__)
            continue
        if found and (param.kind != inspect.Parameter.VAR_POSITIONAL and param.kind != inspect.Parameter.KEYWORD_ONLY and param.kind != inspect.Parameter.VAR_KEYWORD):
            raise ValueError('request parameter must be the last named parameter in function: %s%s' % (fn.__name__, str(sig)))
    return found


class RequestHandler(object):

    def __init__(self, app, fn):
        self._app = app
        self._func = fn
        self._has_request_arg = has_request_arg(fn)
        self._has_var_kw_arg = has_var_kw_arg(fn)
        self._has_named_kw_args = has_named_kw_args(fn)
        self._named_kw_args = get_named_kw_args(fn)
        self._required_kw_args = get_requried_kw_args(fn)

    async def __call__(self, request):
        kw = None
        if self._has_var_kw_arg or self._has_named_kw_args or self._required_kw_args:
            if request.method == 'POST':
                if not request.content_type:
                    return web.HTTPBadRequest('Missing Content-Type.')
                ct = request.content_type.lower()
                if ct.startswith('application/json'):
                    params = await request.json()
                    if not isinstance(params, dict):
                        return web.HTTPBadRequest('JSON body must be object')
                    kw = params
                elif ct.startswith('application/x-www-form-urlencoded') or ct.startswith('multipart/form-data'):
                    params = await request.post()
                    kw = dict(**params)
                else:
                    return web.HTTPBadRequest('Unspported Content-Type: %s' % request.content_type)
            if request.method == 'GET':
                qs = request.quere_string
                if qs:
                    kw = dict()
                    for k, v in parse.parse_qs(qs, True).items():
                        kw[k] = v[0]
        if kw is None:
            kw = dict(**request.match_info)
        else:
            if not self._has_var_kw_arg and self._named_kw_args:
                # remove all unamed kw
                copy = dict()
                for name in self._named_kw_args:
                    if name in kw:
                        copy[name] = kw[name]
                kw = copy
            # check named arg:
            for k, v in request.match_info.items():
                if k in kw:
                    logging.warnings('Duplicate arg name in named arg and kw args: %s' % k)
                kw[k] = v
        if self._has_request_arg:
            kw['request'] = request
        # check required kw:
        if self._required_kw_args:
            for name in self._required_kw_args:
                if name not in kw:
                    return web.HTTPBadRequest('Misssing argument: %s' % name)
        logging.info('call with args: %s' % str(kw))
        try:
            r = await self._func(**kw)
            return r
        except APIError as e:
            return dict(error=e.error, data=e.data, message=e.message)


def add_static(app):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    app.router.add_static('/static/', path)
    logging.info('add static %s => %s' % ('/static/', path))


def add_route(app, fn):
    method = getattr(fn, '__method__', None)
    path = getattr(fn, '__route__', None)
    if path is None or method is None:
        raise ValueError('@get or @post note defined in %s.' % str(fn))
    if not asyncio.iscoroutinefunction(fn) and not inspect.isgeneratorfunction(fn):
        fn = asyncio.coroutine(fn)
    logging.info('add route %s %s => %s(%s)' % (method, path, fn.__name__, ','.join(inspect.signature(fn).parameters.keys())))
    app.router.add_route(method, path, RequestHandler(app, fn))


def add_routes(app, module_name):
    n = module_name.rfind('.')
    if n == (-1):
        mod = __import__(module_name, globals(), locals())
    else:
        name = module_name[n + 1:]
        mod = getattr(__import__(module_name[:n], globals(), locals(), [name]), name)
    logging.info('module :%s' % mod.__name__)
    logging.info('dir(module) :%s' % str(dir(mod)))
    for attr in dir(mod):
        logging.info('module: %s' % attr)
        if attr.startswith('_'):
            continue
        fn = getattr(mod, attr)
        if callable(fn):
            logging.info('callable(fn) %s [module:%s]' % (fn.__name__, attr))
            method = getattr(fn, '__method__', None)
            path = getattr(fn, '__route__', None)
            if method and path:
                logging.info('callable(fn) %s attribute[method: %s path: %s]' % (fn.__name__, method, path))
                add_route(app, fn)
