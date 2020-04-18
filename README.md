# gino-aiohttp

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/7579f869992a4b618e115731821e43ee)](https://www.codacy.com/gh/python-gino/gino-aiohttp?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=python-gino/gino-aiohttp&amp;utm_campaign=Badge_Grade)

## Introduction

An extension for GINO to support aiohttp.web server.

## Usage

The common usage looks like this:

```python
from aiohttp import web
from gino.ext.aiohttp import Gino

db = Gino()
app = web.Application(middlewares=[db])
db.init_app(app)
```

