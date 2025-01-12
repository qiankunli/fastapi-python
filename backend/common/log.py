#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import inspect
import logging
from sys import stderr, stdout
from typing import Any

from asgi_correlation_id import correlation_id
from libs.conf import settings
from loguru import logger


class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentation.
    See https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).no
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging():
    """
    From https://pawamoy.github.io/posts/unify-logging-for-a-gunicorn-uvicorn-app/
    https://github.com/pawamoy/pawamoy.github.io/issues/17
    """
    # Intercept everything at the root logger
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(settings.LOG_ROOT_LEVEL)

    # Remove all log handlers and propagate to root logger
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        if 'uvicorn.access' in name or 'watchfiles.main' in name:
            logging.getLogger(name).propagate = False
        else:
            logging.getLogger(name).propagate = True

        # Debug log handlers
        # logging.debug(f'{logging.getLogger(name)}, {logging.getLogger(name).propagate}')

    # Remove every other logger's handlers
    logger.remove()

    # Define the correlation_id filter function
    # https://github.com/snok/asgi-correlation-id?tab=readme-ov-file#configure-logging
    # https://github.com/snok/asgi-correlation-id/issues/7
    def correlation_id_filter(record: dict[str, Any]) -> bool:
        cid = correlation_id.get(settings.LOG_CID_DEFAULT_VALUE)
        if cid:
            record['correlation_id'] = cid[: settings.LOG_CID_UUID_LENGTH]
        return True

    # Configure loguru logger before starts logging
    logger.configure(
        handlers=[
            {
                'sink': stdout,
                'level': settings.LOG_STDOUT_LEVEL,
                'filter': lambda record: correlation_id_filter(record) and record['level'].no <= 25,
                'format': settings.LOG_STD_FORMAT,
            },
            {
                'sink': stderr,
                'level': settings.LOG_STDERR_LEVEL,
                'filter': lambda record: correlation_id_filter(record) and record['level'].no >= 30,
                'format': settings.LOG_STD_FORMAT,
            },
        ]
    )


log = logger
