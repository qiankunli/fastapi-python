from enum import Enum
from typing import List

from common.enum.task import TaskType


class ResourceType(str, Enum):
    """资源类型"""

    VIDEO = "video"
    AUDIO = "audio"
    PICTURE = "picture"

    @property
    def task_types(self) -> List[TaskType]:
        if self == ResourceType.VIDEO:
            return [TaskType.V2A, TaskType.VFE]
        elif self == ResourceType.AUDIO:
            return [TaskType.STT]
        elif self == ResourceType.PICTURE:
            return [TaskType.OCR]
        else:
            raise ValueError(f"Invalid resource type: {self}")
