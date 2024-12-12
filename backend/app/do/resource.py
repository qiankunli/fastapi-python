from datetime import datetime

from pydantic import BaseModel, Field

from app.do.base import DOAttributeBase
from app.model.resource_model import ResourceModel
from common.enum.resource import ResourceType
from utils.str import uuid7_hex


class ResourceMetadata(BaseModel):
    pass


class ResourceConfig(BaseModel):
    pass


class ResourceDO(DOAttributeBase):
    id: str = Field(default_factory=uuid7_hex)
    parent_id: str | None = Field(None)
    queue: str = Field(default='default')
    name: str
    type: ResourceType
    extension: str
    meta_data: ResourceMetadata = Field(
        default_factory=lambda: ResourceMetadata())
    storage_url: str
    config: ResourceConfig = Field(
        default_factory=lambda: ResourceConfig())
    text: str | None = Field(None)
    text_url: str | None = Field(None)
    create_time: datetime = Field(default_factory=datetime.now)
    update_time: datetime = Field(default_factory=datetime.now)

    def do_to_model(self, **kwargs):
        return ResourceModel(**self.model_dump(), **kwargs)
