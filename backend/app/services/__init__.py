from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.dashboard_service import DashboardService
from app.services.api_config_service import ApiConfigService, VINRecognizer
from app.services.log_service import LogService
from app.services.car_model_service import CarModelService
from app.services.group_service import GroupService
from app.services.vin_service import VinRecordService
from app.services.statistics_service import StatisticsService

__all__ = [
    "AuthService",
    "UserService",
    "DashboardService",
    "ApiConfigService",
    "VINRecognizer",
    "LogService",
    "CarModelService",
    "GroupService",
    "VinRecordService",
    "StatisticsService",
]
