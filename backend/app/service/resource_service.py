from app.crud.crud_resource import resource_dao
from app.crud.crud_task import task_dao
from app.do.resource import ResourceDO
from app.do.task import TaskDO
from app.schema.resource_schema import CreateResourceRequest
from common.exception import errors
from common.log import log
from utils.str import uuid7_hex


class ResourceService:
    @staticmethod
    def get(id: str) -> ResourceDO:
        resource = resource_dao.select_model_by_column("id", id)
        if not resource:
            raise errors.NotFoundError(msg='资源不存在')
        return ResourceDO.from_orm(resource)

    @staticmethod
    def create(request: CreateResourceRequest) -> None:
        if request.id is None:
            request.id = uuid7_hex()
        resource = ResourceDO(**request.model_dump())
        resource_dao.create_model(resource)
        log.info(f'create resource {resource.name} {resource.id}')
        for task_type in resource.type.task_types:
            task = TaskDO(resource_id=resource.id, queue=request.queue, type=task_type.value)
            task_dao.create_model(task)
            log.info(f'create task {resource.name} {task_type}')


resource_service: ResourceService = ResourceService()
