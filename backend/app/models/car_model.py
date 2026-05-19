"""
car_model模型模块
定义car_model表结构
"""

from sqlalchemy import Column, String, Integer, Text, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseModel


# 多对多关联表
car_model_supplier = Table(
    "car_model_supplier",
    Base.metadata,
    Column("supplier_id", Integer, ForeignKey("suppliers.id")),
    Column("car_model_id", Integer, ForeignKey("car_models.id"))
)


class MemberType(BaseModel):
    """成员类型表"""
    __tablename__ = "member_types"
    __table_args__ = {"comment": "成员类型表 - 存储供应商成员类型"}

    name = Column(String(50), nullable=False, comment="类型名称")
    description = Column(Text, nullable=True, comment="类型描述")


class Supplier(BaseModel):
    """汽配商表"""
    __tablename__ = "suppliers"

    wxid = Column(String(100), unique=True, nullable=False, comment="汽配商wxid")
    name = Column(String(200), nullable=False, comment="汽配商名称")
    member_type_id = Column(Integer, ForeignKey("member_types.id", comment="主键ID"), nullable=True, comment="成员类型ID")

    # 关联
    member_type = relationship("MemberType")
    car_models = relationship("CarModel", secondary=car_model_supplier, back_populates="suppliers")


class CarModel(BaseModel):
    """车型表"""
    __tablename__ = "car_models"

    name = Column(String(200), nullable=False, comment="车型名称")
    brand = Column(String(100), nullable=True, comment="品牌")
    series = Column(String(100), nullable=True, comment="车系")
    displacement = Column(String(50), nullable=True, comment="排量")
    year = Column(String(20), nullable=True, comment="年份")

    # 关联
    suppliers = relationship("Supplier", secondary=car_model_supplier, back_populates="car_models")
