from datetime import datetime, timedelta, date
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, and_, case
from app.models.statistics import Statistics


class AccountService:
    """账户管理服务 - LLM识别统计"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_llm_stats(self) -> Dict:
        """获取LLM识别统计数据"""
        # 总成功次数
        success_result = await self.db.execute(
            select(func.count(Statistics.id)).where(
                and_(
                    Statistics.is_deleted == False,
                    Statistics.recognize_status == "success"
                )
            )
        )
        success_count = success_result.scalar() or 0

        # 总失败次数
        fail_result = await self.db.execute(
            select(func.count(Statistics.id)).where(
                and_(
                    Statistics.is_deleted == False,
                    Statistics.recognize_status == "fail"
                )
            )
        )
        fail_count = fail_result.scalar() or 0

        # 计算成功率
        total_count = success_count + fail_count
        success_rate = round((success_count / total_count * 100), 1) if total_count > 0 else 0.0

        return {
            "success_count": success_count,
            "fail_count": fail_count,
            "success_rate": success_rate
        }

    async def get_daily_stats(
        self,
        start_date: date = None,
        end_date: date = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict:
        """获取每日识别统计"""
        if not end_date:
            end_date = datetime.now().date()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        # 构建查询 - 使用SQLAlchemy 2.0兼容语法
        query = select(
            func.date(Statistics.date).label("stat_date"),
            func.count(Statistics.id).label("total_count"),
            func.sum(case((Statistics.recognize_status == "success", 1), else_=0)).label("success_count"),
            func.sum(case((Statistics.recognize_status == "fail", 1), else_=0)).label("fail_count")
        ).where(
            and_(
                Statistics.is_deleted == False,
                func.date(Statistics.date) >= start_date,
                func.date(Statistics.date) <= end_date
            )
        ).group_by(
            func.date(Statistics.date)
        ).order_by(
            func.date(Statistics.date).desc()
        )

        # 获取总数
        count_query = select(func.count(func.distinct(func.date(Statistics.date)))).where(
            and_(
                Statistics.is_deleted == False,
                func.date(Statistics.date) >= start_date,
                func.date(Statistics.date) <= end_date
            )
        )
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # 分页
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        rows = result.all()

        # 格式化数据
        daily_stats = []
        for row in rows:
            total_count = row.total_count or 0
            success_count = int(row.success_count) if row.success_count else 0
            fail_count = int(row.fail_count) if row.fail_count else 0
            success_rate = round((success_count / total_count * 100), 1) if total_count > 0 else 0.0

            daily_stats.append({
                "date": row.stat_date.strftime("%Y-%m-%d"),
                "count": total_count,
                "success_count": success_count,
                "fail_count": fail_count,
                "success_rate": success_rate
            })

        return {
            "list": daily_stats,
            "total": total,
            "page": page,
            "page_size": page_size
        }
