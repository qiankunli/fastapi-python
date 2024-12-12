from typing import Annotated

from fastapi import APIRouter, Path

from app.schema.resource_schema import CreateResourceRequest
from app.service.resource_service import resource_service
from common.response.response_schema import ResponseModel, response_base


router = APIRouter(prefix="/resources")


@router.get('/{id}', summary='获取资源详情')
async def get_resource(id: Annotated[str, Path(...)]) -> ResponseModel:
    api = resource_service.get(id=id)
    return response_base.success(data=api)


@router.post('', summary='创建资源')
async def create_resource(reqeust: CreateResourceRequest) -> ResponseModel:
    resource_service.create(reqeust)
    return response_base.success()
