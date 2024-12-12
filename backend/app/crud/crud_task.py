#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import List

from sqlalchemy import func, select, update

from app.model.task_model import TaskModel
from common.enum.task import TaskStatus
from libs.conf import settings
from libs.database.session import get_session
from pkg.crud_plus.crud import CRUDPlus


class CRUDTask(CRUDPlus[TaskModel]):

    def list_by_queue(self):
        session = get_session()
        query = select(TaskModel.queue, func.min(TaskModel.id)).filter(
            TaskModel.run_time <= func.now(),
            TaskModel.retry_count <= settings.TASK_RETRY_COUNT,
            TaskModel.status <= TaskStatus.PENDING.value,
        ).group_by(TaskModel.queue)
        result = session.execute(query)
        return result.scalars().all()

    def list_by_ids(self, task_ids: List[str]):
        session = get_session()
        query = select(self.model).filter(
            TaskModel.id.in_(task_ids)
        )
        result = session.execute(query)
        return result.scalars().all()

    def set_task_running_if_not(self, task_id: int) -> int:
        session = get_session()
        query = update(self.model).filter(
            TaskModel.id == task_id,
            TaskModel.status == TaskStatus.PENDING.value
        ).values(
            {
                TaskModel.status: TaskStatus.RUNNING.value
            }
        )
        result = session.execute(query)
        return result.rowcount


task_dao: CRUDTask = CRUDTask(TaskModel)
