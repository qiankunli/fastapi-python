#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import copy
import sys
import time
from functools import wraps
from typing import Any, Mapping
from urllib.parse import quote_plus

from pymysql.connections import CLIENT
from sqlalchemy import URL, Engine, create_engine, exc, orm as sa_orm

from common.log import log
from libs.conf import settings


engine_args: Mapping[str, Any] = dict(
    future=True,
    pool_size=50,
    pool_recycle=3600,
    pool_pre_ping=True,  # 是否在使用连接前先进行ping, https://docs.sqlalchemy.org/en/14/core/pooling.html#pool-disconnects
    max_overflow=100,
    pool_timeout=20,
)


def ensure_connection(func):
    """装饰器：确保执行数据库操作前连接是健康的"""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except exc.OperationalError as e:
            if "Lost connection" in str(e):
                log.warning(f"Lost connection during {func.__name__}, attempting to reconnect...")
                self.ensure_healthy_connection()
                # 重试操作
                return func(self, *args, **kwargs)
            raise

    return wrapper


class HealthySession(sa_orm.Session):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ping_query = "SELECT 1"  # 用于健康检查的简单查询
        self._last_check_time: int = 0
        self.check_interval = 60  # 连接检查间隔（秒）
        self.max_retries = 3  # 最大重试次数

    def should_check_connection(self):
        """判断是否需要检查连接（基于时间间隔）"""
        current_time = int(time.time())
        if current_time - self._last_check_time > self.check_interval:
            self._last_check_time = current_time
            return True
        return False

    def is_connection_valid(self):
        """检查数据库连接是否有效"""
        try:
            # 执行一个简单的查询来测试连接
            self.execute(self.ping_query)
            return True
        except exc.OperationalError as e:
            log.warning(f"Database connection check failed: {str(e)}")
            return False
        except Exception as e:
            log.error(f"Unexpected error during connection check: {str(e)}")
            return False

    def ensure_healthy_connection(self):
        """确保连接健康，如果不健康则重新连接"""
        if not self.is_connection_valid():
            log.info("Detected invalid connection, disposing engine...")
            if not self.bind:
                raise exc.UnboundExecutionError(
                    "Cannot dispose connection - no valid engine found"
                )
            # 释放所有连接
            self.bind.dispose()  # type: ignore
            # 执行一个查询来触发新连接的建立
            self.execute(self.ping_query)
            log.info("New connection established")

    @ensure_connection
    def execute(self, *args, **kwargs):
        return super().execute(*args, **kwargs)

    @ensure_connection
    def commit(self):
        try:
            super().commit()
        except exc.OperationalError as e:
            log.error(f"Error during commit: {str(e)}")
            raise
        except Exception as e:
            log.error(f"Unexpected error during commit: {str(e)}")
            raise

    @ensure_connection
    def rollback(self):
        try:
            super().rollback()
        except exc.OperationalError as e:
            log.error(f"Error during rollback: {str(e)}")
            raise
        except Exception as e:
            log.error(f"Unexpected error during rollback: {str(e)}")
            raise


def create_engine_and_session(url: str | URL, autocommit: bool = False) -> \
        tuple[Engine, sa_orm.sessionmaker[sa_orm.Session]]:
    try:
        args = dict(copy.deepcopy(engine_args))
        if autocommit:
            args['isolation_level'] = 'AUTOCOMMIT'
        # 数据库引擎
        engine = create_engine(
            url,
            echo=settings.DB_ECHO,
            **args,
            connect_args={
                "client_flag": CLIENT.MULTI_STATEMENTS,
            },
        )

    except Exception as e:
        log.error('❌ 数据库链接失败 {}', e)
        sys.exit()
    else:
        session = sa_orm.sessionmaker(
            bind=engine,
            autoflush=False,
            expire_on_commit=True,
            class_=HealthySession,
        )
        return engine, session  # type: ignore


SQLALCHEMY_DATABASE_URL = (
    f'mysql+pymysql://{settings.DB_USERNAME}:{quote_plus(settings.DB_PASSWORD)}@{settings.DB_HOST}:'
    f'{settings.DB_PORT}/{settings.DB_DATABASE}?charset={settings.DB_CHARSET}'
)

engine, db_session = create_engine_and_session(SQLALCHEMY_DATABASE_URL)

engine_auto, db_session_auto = create_engine_and_session(SQLALCHEMY_DATABASE_URL, autocommit=True)

# 不同线程初始化不同的session实例
worker_session = sa_orm.scoped_session(db_session)

worker_session_auto = sa_orm.scoped_session(db_session_auto)
