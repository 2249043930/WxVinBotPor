from app.crud.base import CRUDBase
from app.crud.user import user_crud
from app.crud.log import log_crud, operation_log_crud
from app.crud.account import account_crud
from app.crud.statistics import statistics_crud
from app.crud.message import message_crud
from app.crud.car_model import member_type_crud, supplier_crud, car_model_crud
from app.crud.group import group_crud
from app.crud.vin_info import vin_info_crud
from app.crud.vin_record import vin_record

__all__ = [
    "CRUDBase",
    "user_crud",
    "log_crud",
    "operation_log_crud",
    "account_crud",
    "statistics_crud",
    "message_crud",
    "member_type_crud",
    "supplier_crud",
    "car_model_crud",
    "group_crud",
    "vin_info_crud",
    "vin_record",
]
