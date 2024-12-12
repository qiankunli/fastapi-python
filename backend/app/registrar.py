#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from multiprocessing import Queue

from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware

from app.api.router import v1 as v1_router
from app.task.task_consumer import TaskConsumer
from app.task.task_producer import TaskProducer
from common.exception.exception_handler import register_exception
from common.log import setup_logging
from common.response.response_schema import ResponseModel
from fastapi_pagination import add_pagination
from libs.conf import settings
from libs.database.db_mysql import SQLALCHEMY_DATABASE_URL
from utils.health_check import ensure_unique_route_names
from utils.serializers import MsgSpecJSONResponse


def register_app():
    # FastAPI
    app = FastAPI(
        title="merlin",
        version="0.0.1",
        description="merlin",
        docs_url="/v1/docs",
        redoc_url="/v1/redocs",
        openapi_url="/v1/openapi",
        default_response_class=MsgSpecJSONResponse,
    )

    # 日志
    register_logger()

    # 中间件
    register_middleware(app)

    # 路由
    register_router(app)

    # 分页
    register_page(app)

    # 全局异常处理
    register_exception(app)

    queue: Queue = Queue(maxsize=settings.TASK_CONCURRENCY)
    task_producer = TaskProducer(queue)
    task_producer.start()
    task_consumer = TaskConsumer(queue)
    task_consumer.start()

    return app


def register_logger() -> None:
    """
    系统日志

    :return:
    """
    setup_logging()


def register_middleware(app: FastAPI):
    """
    中间件，执行顺序从下往上

    :param app:
    :return:
    """
    app.add_middleware(DBSessionMiddleware, commit_on_exit=True, db_url=SQLALCHEMY_DATABASE_URL,
                       engine_args={  # engine arguments example
                           "echo": settings.DB_ECHO,  # print all SQL statements
                           "pool_pre_ping": True,
                           # feature will normally emit SQL equivalent to “SELECT 1” each time a connection is
                           # checked out from the pool
                           "pool_size": 5,  # number of connections to keep open at a time
                           "max_overflow": 10,  # number of connections to allow to be opened above pool_size
                       }, )


def register_router(app: FastAPI):
    """
    路由

    :param app: FastAPI
    :return:
    """

    @app.get("/health")
    def health() -> ResponseModel:
        return ResponseModel(data={"status": "ok"})

    # API
    app.include_router(v1_router)

    # Extra
    ensure_unique_route_names(app)


def register_page(app: FastAPI):
    """
    分页查询

    :param app:
    :return:
    """
    add_pagination(app)
