from datetime import datetime

from pydantic import Field

from app.do.base import DOAttributeBase
from app.model.task_model import TaskModel
from common.enum.task import TaskStatus


class TaskDO(DOAttributeBase):
    # 插入时id 不作数，只是查询时需要
    id: int = 0
    resource_id: str
    parent_resource_id: str | None = Field(None)
    queue: str = Field(default='default')
    type: str
    status: int = Field(TaskStatus.PENDING.value)
    retry_count: int = Field(0)
    error_msg: str | None = Field(None)
    run_time: datetime = Field(default_factory=datetime.now)
    create_time: datetime = Field(default_factory=datetime.now)
    update_time: datetime = Field(default_factory=datetime.now)

    def do_to_model(self, **kwargs):
        return TaskModel(resource_id=self.resource_id,
                         parent_resource_id=self.parent_resource_id,
                         queue=self.queue,
                         type=self.type,
                         status=self.status,
                         retry_count=self.retry_count,
                         error_msg=self.error_msg)
