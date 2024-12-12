from fastapi_sqlalchemy import db as fastapi_db
from fastapi_sqlalchemy.exceptions import (
    MissingSessionError,
    SessionNotInitialisedError,
)

from libs.database.db_mysql import worker_session_auto


def get_session():
    try:
        s = fastapi_db.session
        if s is None:
            raise MissingSessionError
        return s
    except (MissingSessionError, SessionNotInitialisedError):
        # 等到这个路径的时候，因为没有fastapi middleware 帮忙，session改用自动commit机制
        return worker_session_auto
