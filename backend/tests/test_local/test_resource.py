import pytest

from app.schema.resource_schema import CreateResourceRequest
from app.service.resource_service import resource_service
from common.enum.resource import ResourceType


@pytest.mark.asyncio
async def test_create_resource():
    resource_service.create(
        CreateResourceRequest(name="123", extension="mp3", storage_url="/abc", type=ResourceType.AUDIO))
    print("end")
