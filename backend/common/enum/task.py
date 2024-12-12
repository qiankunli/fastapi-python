from enum import Enum


class TaskType(str, Enum):
    """任务类型"""

    STT = "stt"
    OCR = "ocr"
    V2A = "v2a"
    # Video Frame Extraction
    VFE = "vfe"


class TaskStatus(int, Enum):
    """任务状态"""
    PENDING = 0
    RUNNING = 1
    SUCCESS = 10
    FAILED = 20
    CANCEL = 30
