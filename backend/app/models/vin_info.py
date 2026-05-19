"""
VIN信息表
存储查询过的车架号信息，用于本地缓存
"""

from sqlalchemy import Column, String, Integer, Text, DateTime
from app.models.base import BaseModel
from datetime import datetime


class VinInfo(BaseModel):
    """VIN信息表 - 存储车辆详细信息"""
    __tablename__ = "vin_info"
    __table_args__ = {"comment": "VIN信息表 - 存储车架号查询结果"}

    # VIN码（主键）
    vin_code = Column(String(17), unique=True, nullable=False, index=True, comment="车架号VIN")

    # 车辆基本信息
    manufacturer = Column(String(100), nullable=True, comment="厂商")
    brand = Column(String(100), nullable=True, comment="品牌")
    car_model = Column(String(200), nullable=True, comment="车型名称")
    series = Column(String(100), nullable=True, comment="车系")
    displacement = Column(String(50), nullable=True, comment="排量")
    year = Column(String(20), nullable=True, comment="年份")

    # 详细配置信息
    typename = Column(String(100), nullable=True, comment="车辆类型")
    enginemodel = Column(String(100), nullable=True, comment="发动机型号")
    sizetype = Column(String(100), nullable=True, comment="车辆尺寸类型")
    geartype = Column(String(100), nullable=True, comment="变速箱类型")
    fronttiresize = Column(String(100), nullable=True, comment="前轮尺寸")
    reartiresize = Column(String(100), nullable=True, comment="后轮尺寸")

    # 机油建议（温馨建议）
    volume = Column(String(50), nullable=True, comment="机油用量")
    viscosity = Column(String(50), nullable=True, comment="机油粘度")
    grade = Column(String(50), nullable=True, comment="机油等级")
    level = Column(String(50), nullable=True, comment="机油级别")

    # 数据来源
    source = Column(String(50), nullable=True, default="jisu_api", comment="数据来源")

    # 查询次数（用于统计）
    query_count = Column(Integer, default=1, comment="查询次数")

    # 最后查询时间
    last_query_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="最后查询时间")

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "vin": self.vin_code,
            "manufacturer": self.manufacturer,
            "brand": self.brand,
            "model_info": self.car_model,
            "series": self.series,
            "displacement": self.displacement,
            "year": self.year,
            "typename": self.typename,
            "enginemodel": self.enginemodel,
            "sizetype": self.sizetype,
            "geartype": self.geartype,
            "fronttiresize": self.fronttiresize,
            "reartiresize": self.reartiresize,
            "volume": self.volume,
            "viscosity": self.viscosity,
            "grade": self.grade,
            "level": self.level,
            "source": self.source,
            "query_count": self.query_count,
            "last_query_time": self.last_query_time.strftime("%Y-%m-%d %H:%M:%S") if self.last_query_time else None
        }
