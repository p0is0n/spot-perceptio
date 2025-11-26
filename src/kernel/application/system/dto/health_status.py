from enum import Enum

class HealthStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
