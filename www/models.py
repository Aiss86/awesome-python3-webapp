#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import time
import uuid
import logging
import asyncio
import orm
import hashlib
from orm import Model, StringField, BooleanField, FloatField, TextField 
from apis import APIValueError


def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)


class User(Model):
    __table__ = 'users'
    logging.info('[Model User]')
    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    email = StringField(ddl='varchar(50)')
    passwd = StringField(ddl='varchar(50)')
    admin = BooleanField()
    name = StringField(ddl='varchar(50)')
    image = StringField(ddl='varchar(500)')
    created_at = FloatField(default=time.time)


class Blog(Model):
    __table__ = 'blogs'
    logging.info('[Model Blog]')
    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    name = StringField(ddl='varchar(50)')
    summary = StringField(ddl='varchar(200)')
    content = TextField()
    created_at = FloatField(default=time.time)


class Comment(Model):
    __table__ = 'comments'
    logging.info('[Model Comment]')
    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    blog_id = StringField(ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    content = TextField()
    created_at = FloatField(default=time.time)


async def test(loop):
    await orm.create_pool(loop=loop, user='root', password='123456', db='awesome')
    u = User(name='Test', email='test@example.com', passwd='1234567890', image='about:blank')
    await u.save()


async def add_admin(loop):
    await orm.create_pool(loop=loop, user='root', password='123456', db='awesome')
    users = await User.findAll('name=?', ['admin'])
    users_num = len(users)
    name = 'admin'
    email = 'admin@123456.com'
    image = 'about:blank'
    admin = True
    init_passwd = '12345678'
    if users_num == 0:
        id = next_id()
        sha1 = hashlib.sha1()
        sha1.update(id.encode('utf-8'))
        sha1.update(b':')
        sha1.update(init_passwd.encode('utf-8'))
        password = sha1.hexdigest()
        u = User(name=name, id=id, email=email, passwd=password, image=image, admin=admin)
        await u.save()
    elif users_num == 1:
        user = users[0]
        id = user.id
        sha1 = hashlib.sha1()
        sha1.update(id.encode('utf-8'))
        sha1.update(b':')
        sha1.update(init_passwd.encode('utf-8'))
        password = sha1.hexdigest()
        created_at = FloatField(time.time)
        u = User(name=name, id=id, email=email, passwd=password, image=image, admin=admin, created_at=created_at)
        await u.update()
    else:
        raise APIValueError('admin', 'data error')

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(add_admin(loop))
