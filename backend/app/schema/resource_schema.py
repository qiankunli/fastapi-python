from pydantic import Field

from app.do.resource import ResourceConfig, ResourceMetadata
from common.enum.resource import ResourceType
from common.schema import SchemaBase


class CreateResourceRequest(SchemaBase):
    # 可以指定resource_id，不指定则自动生成
    id: str | None = None
    name: str = Field(description='名称')
    queue: str = Field(default='default', description='分组')
    extension: str = Field(description='扩展名')
    storage_url: str = Field(description='存储地址')
    type: ResourceType = Field(description='资源类型')
    meta_data: ResourceMetadata | None = Field(default_factory=ResourceMetadata, description='元数据')
    config: ResourceConfig | None = Field(default_factory=ResourceConfig, description='处理配置')
