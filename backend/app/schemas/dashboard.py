from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any


class DashboardStats(BaseModel):
    """数据看板统计"""
    model_config = ConfigDict(populate_by_name=True)

    totalVehicles: int = 0
    monthNew: int = 0
    monthGrowth: float = 0.0
    weekNew: int = 0
    weekGrowth: float = 0.0
    todayNew: int = 0
    groupCount: int = 0
    llmSuccessRate: float = 0.0


class ChartData(BaseModel):
    """图表数据"""
    vehicleTypePie: List[Dict[str, Any]] = []
    topModelsBar: List[Dict[str, Any]] = []
    displacementStats: List[Dict[str, Any]] = []
    trendLine: List[Dict[str, Any]] = []
