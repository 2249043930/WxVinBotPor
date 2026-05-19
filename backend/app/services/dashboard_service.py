from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from app.crud.statistics import statistics_crud
from app.crud.group import group_crud
from app.crud.account import account_crud
from app.models.statistics import Statistics
from app.models.vin_info import VinInfo
from app.schemas.dashboard import DashboardStats, ChartData


class DashboardService:
    """数据看板服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_stats(self) -> DashboardStats:
        """获取看板统计数据 - 从vin_info表获取真实数据"""
        now = datetime.utcnow()

        # 总车辆数（从vin_info表）
        total_result = await self.db.execute(
            select(func.count(VinInfo.id))
        )
        total_vehicles = total_result.scalar() or 0

        # 本月新增（按created_at统计）
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_result = await self.db.execute(
            select(func.count(VinInfo.id)).where(
                VinInfo.created_at >= month_start
            )
        )
        month_new = month_result.scalar() or 0

        # 上月对比
        last_month_start = (month_start - timedelta(days=30)).replace(day=1)
        last_month_result = await self.db.execute(
            select(func.count(VinInfo.id)).where(
                VinInfo.created_at >= last_month_start,
                VinInfo.created_at < month_start
            )
        )
        last_month_count = last_month_result.scalar() or 0
        month_growth = 0.0
        if last_month_count > 0:
            month_growth = (month_new - last_month_count) / last_month_count

        # 本周新增
        week_start = now - timedelta(days=now.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_result = await self.db.execute(
            select(func.count(VinInfo.id)).where(
                VinInfo.created_at >= week_start
            )
        )
        week_new = week_result.scalar() or 0

        # 上周对比
        last_week_start = week_start - timedelta(days=7)
        last_week_result = await self.db.execute(
            select(func.count(VinInfo.id)).where(
                VinInfo.created_at >= last_week_start,
                VinInfo.created_at < week_start
            )
        )
        last_week_count = last_week_result.scalar() or 0
        week_growth = 0.0
        if last_week_count > 0:
            week_growth = (week_new - last_week_count) / last_week_count

        # 今日新增
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_result = await self.db.execute(
            select(func.count(VinInfo.id)).where(
                VinInfo.created_at >= today_start
            )
        )
        today_new = today_result.scalar() or 0

        # 群聊数量
        groups = await group_crud.get_active_groups(self.db)
        group_count = len(groups)

        # LLM识别成功率（从statistics表计算）
        llm_success_rate = 0.0
        stats_result = await self.db.execute(
            select(func.count(Statistics.id)).where(Statistics.is_deleted == False)
        )
        total_stats = stats_result.scalar() or 0
        if total_stats > 0:
            success_result = await self.db.execute(
                select(func.count(Statistics.id)).where(
                    Statistics.is_deleted == False,
                    Statistics.recognize_status == "success"
                )
            )
            success_count = success_result.scalar() or 0
            llm_success_rate = success_count / total_stats

        return DashboardStats(
            totalVehicles=total_vehicles,
            monthNew=month_new,
            monthGrowth=round(month_growth * 100, 2),
            weekNew=week_new,
            weekGrowth=round(week_growth * 100, 2),
            todayNew=today_new,
            groupCount=group_count,
            llmSuccessRate=round(llm_success_rate * 100, 2)
        )

    async def get_chart_data(self, chart_type: str = "all", days: int = 30) -> ChartData:
        """获取图表数据 - 从vin_info表获取真实数据"""
        now = datetime.utcnow()
        start_date = now - timedelta(days=days)

        chart_data = ChartData()

        if chart_type in ["all", "vehicle_type"]:
            # 车辆类型统计（从typename字段）
            type_result = await self.db.execute(
                select(VinInfo.typename, func.count(VinInfo.id))
                .where(VinInfo.typename != None)
                .group_by(VinInfo.typename)
            )
            type_data = type_result.all()
            if type_data:
                chart_data.vehicleTypePie = [
                    {"name": name or "未知", "value": count}
                    for name, count in type_data
                ]
            else:
                chart_data.vehicleTypePie = []

        if chart_type in ["all", "top_models"]:
            # 热门车型排行（按query_count排序）
            model_result = await self.db.execute(
                select(VinInfo.car_model, VinInfo.query_count)
                .where(VinInfo.car_model != None)
                .order_by(VinInfo.query_count.desc())
                .limit(10)
            )
            model_data = model_result.all()
            if model_data:
                chart_data.topModelsBar = [
                    {"name": name or "未知", "value": count or 1}
                    for name, count in model_data
                ]
            else:
                chart_data.topModelsBar = []

        if chart_type in ["all", "displacement"]:
            # 排量分布
            disp_result = await self.db.execute(
                select(VinInfo.displacement, func.count(VinInfo.id))
                .where(VinInfo.displacement != None)
                .group_by(VinInfo.displacement)
            )
            disp_data = disp_result.all()
            if disp_data:
                chart_data.displacementStats = [
                    {"name": name or "未知", "value": count}
                    for name, count in disp_data
                ]
            else:
                chart_data.displacementStats = []

        if chart_type in ["all", "trend"]:
            # 新增趋势（按天统计created_at）
            trend_data = []
            for i in range(days):
                date = start_date + timedelta(days=i)
                next_date = date + timedelta(days=1)
                count_result = await self.db.execute(
                    select(func.count(VinInfo.id)).where(
                        VinInfo.created_at >= date,
                        VinInfo.created_at < next_date
                    )
                )
                count = count_result.scalar() or 0
                trend_data.append({
                    "date": date.strftime("%m-%d"),
                    "value": count
                })
            chart_data.trendLine = trend_data

        return chart_data

    async def get_recent_records(self, limit: int = 10):
        """获取最近识别记录"""
        result = await self.db.execute(
            select(VinInfo)
            .order_by(VinInfo.created_at.desc())
            .limit(limit)
        )
        records = result.scalars().all()
        return [
            {
                "id": r.id,
                "vin": r.vin_code,
                "model": r.car_model,
                "createTime": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else None,
                "status": 1  # 成功
            }
            for r in records
        ]

    async def get_hot_models(self, limit: int = 10):
        """获取热门车型排行"""
        result = await self.db.execute(
            select(VinInfo.car_model, VinInfo.query_count)
            .where(VinInfo.car_model != None)
            .order_by(VinInfo.query_count.desc())
            .limit(limit)
        )
        models = result.all()
        return [
            {
                "rank": i + 1,
                "modelName": name or "未知",
                "count": count or 1,
                "trend": 0  # 暂时不计算趋势
            }
            for i, (name, count) in enumerate(models)
        ]
