"""
群聊配置模型
存储每个群聊的客服配置和车型-供应商绑定
"""

from sqlalchemy import Column, String, Integer, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseModel


# 群聊-车型-供应商绑定关联表
group_model_supplier = Table(
    "group_model_supplier",
    Base.metadata,
    Column("group_config_id", Integer, ForeignKey("group_configs.id")),
    Column("car_model_id", Integer, ForeignKey("car_models.id")),
    Column("supplier_id", Integer, ForeignKey("suppliers.id"))
)


class GroupConfig(BaseModel):
    """群聊配置表 - 存储每个群的客服和车型供应商绑定"""
    __tablename__ = "group_configs"
    __table_args__ = {"comment": "群聊配置表 - 存储群客服和车型供应商绑定"}

    # 群聊信息
    group_id = Column(String(200), unique=True, nullable=False, index=True, comment="微信群ID")
    group_name = Column(String(200), nullable=True, comment="微信群名称")

    # 客服配置
    customer_service_wxid = Column(String(100), nullable=True, comment="客服wxid")
    customer_service_name = Column(String(100), nullable=True, comment="客服名称")

    # 关联 - 车型-供应商绑定（通过关联表）
    model_suppliers = relationship("GroupModelSupplier", back_populates="group_config", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "group_id": self.group_id,
            "group_name": self.group_name,
            "customer_service_wxid": self.customer_service_wxid,
            "customer_service_name": self.customer_service_name,
            "model_suppliers": [ms.to_dict() for ms in self.model_suppliers] if self.model_suppliers else [],
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None
        }


class GroupModelSupplier(BaseModel):
    """群聊车型供应商绑定表 - 每个群的不同车型绑定不同供应商"""
    __tablename__ = "group_model_suppliers"
    __table_args__ = {"comment": "群聊车型供应商绑定表"}

    # 外键
    group_config_id = Column(Integer, ForeignKey("group_configs.id"), nullable=False, comment="群聊配置ID")
    car_model_id = Column(Integer, ForeignKey("car_models.id"), nullable=False, comment="车型ID")
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, comment="供应商ID")

    # 关联
    group_config = relationship("GroupConfig", back_populates="model_suppliers")
    car_model = relationship("CarModel")
    supplier = relationship("Supplier")

    def to_dict(self):
        return {
            "id": self.id,
            "car_model_id": self.car_model_id,
            "car_model_name": self.car_model.name if self.car_model else None,
            "supplier_id": self.supplier_id,
            "supplier_wxid": self.supplier.wxid if self.supplier else None,
            "supplier_name": self.supplier.name if self.supplier else None
        }
