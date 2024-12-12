#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import JSON, TEXT, String
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from common.model import Base
from utils.str import uuid7_hex


class ResourceModel(Base):
    """资源"""

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return 'resource'
    # 自建的id 不带横杠，但是保不齐传入的id带横杠，所以长度还是36
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default_factory=uuid7_hex)
    parent_id: Mapped[str] = mapped_column(String(36), index=True, default=None, nullable=True, comment='父资源id')
    queue: Mapped[str] = mapped_column(String(32), default='default', nullable=False, comment='分组')
    name: Mapped[str] = mapped_column(String(50), index=True, default=None, nullable=False, comment='名称')
    type: Mapped[str] = mapped_column(String(50), default=None, nullable=False, comment='类型')
    extension: Mapped[str] = mapped_column(String(32), default=None, nullable=False, comment='扩展名')
    meta_data: Mapped[dict | None] = mapped_column(JSON, default=None, comment='元信息')
    storage_url: Mapped[str | None] = mapped_column(String(255), default=None, nullable=False, comment='存储地址')
    config: Mapped[dict | None] = mapped_column(JSON, default=None, comment='转换配置')
    text: Mapped[str] = mapped_column(TEXT, default=None, comment='转换结果')
    text_url: Mapped[str | None] = mapped_column(String(255), default=None, comment='text存储地址')

    def __repr__(self):
        return (f"<Resource(id='{self.id}', parent_id='{self.parent_id}', "
                f"storage_url='{self.storage_url}', config='{self.config}')>"
                f" create_time='{self.create_time}')>")
