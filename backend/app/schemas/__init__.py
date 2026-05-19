from app.schemas.base import BaseSchema, PaginationParams, PaginationResponse, ResponseModel
from app.schemas.auth import Token, LoginRequest
from app.schemas.user import UserBase, UserCreate, UserUpdate, UserResponse, UserList
from app.schemas.api_config import ApiConfig, ApiConfigCreate, ApiConfigUpdate, ApiConfigList, VINRecognitionResult
from app.schemas.log import LogRecord, LogList, OperationLogRecord
from app.schemas.dashboard import DashboardStats, ChartData
from app.schemas.car_model import MemberType, MemberTypeCreate, Supplier, SupplierCreate, CarModel, CarModelCreate
from app.schemas.group import WechatGroup, WechatGroupCreate, WechatGroupUpdate
from app.schemas.vin import VinRecord, VinRecordList, VinRecordDetail

__all__ = [
    "BaseSchema",
    "PaginationParams",
    "PaginationResponse",
    "ResponseModel",
    "Token",
    "LoginRequest",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserList",
    "ApiConfig",
    "ApiConfigCreate",
    "ApiConfigUpdate",
    "ApiConfigList",
    "VINRecognitionResult",
    "LogRecord",
    "LogList",
    "OperationLogRecord",
    "DashboardStats",
    "ChartData",
    "MemberType",
    "MemberTypeCreate",
    "Supplier",
    "SupplierCreate",
    "CarModel",
    "CarModelCreate",
    "WechatGroup",
    "WechatGroupCreate",
    "WechatGroupUpdate",
    "VinRecord",
    "VinRecordList",
    "VinRecordDetail",
]
