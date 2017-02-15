#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random

import settings


class RamdomUserAgent(object):

    def __init__(self):
        self.agents = settings.USER_AGENTS

    def process_request(self, request, spider):
        request.headers.setdefault('User-Agent', random.choice(self.agents))


class ProxyMiddleWare(object):
    pass
