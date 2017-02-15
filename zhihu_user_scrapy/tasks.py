#!/usr/bin/env python
# -*- coding: utf-8 -*-
from io import BytesIO
import requests
from PIL import Image
from celery import Celery


app = Celery('cele', broker='redis://localhost:6379')


@app.task
def download(url, path='images'):
    res = requests.get(url)
    filename = url[url.rfind('/')+1:]
    with open('{0}/{1}'.format(path, filename), 'w') as img:
        img.write(res.content)