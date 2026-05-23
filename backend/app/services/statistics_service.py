from typing import Optional, List, Dict
from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, and_, outerjoin
from app.crud.message import message_crud
from app.models.message import MessageRecord
from app.models.group_config import GroupConfig


class StatisticsService:
    """统计服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_group_activity_stats(
        self,
        days: int = 30,
        limit: int = 10
    ) -> Dict:
        """获取群活跃度统计数据
        
        统计包含车架号图片的消息数量，按群分组
        
        Args:
            days: 统计天数（默认30天）
            limit: 返回前N个活跃群（默认10个）
            
        Returns:
            Dict: 群活跃度统计数据
        """
        # 计算起始日期
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 查询每个群的VIN消息数量（关联group_configs获取群聊昵称）
        query = (
            select(
                MessageRecord.source_group,
                func.coalesce(GroupConfig.group_name, MessageRecord.source_group).label('display_name'),
                func.count(MessageRecord.id).label('message_count')
            )
            .outerjoin(
                GroupConfig,
                MessageRecord.source_group == GroupConfig.group_id
            )
            .where(
                and_(
                    MessageRecord.vin_code.isnot(None),
                    MessageRecord.msg_date >= start_date,
                    MessageRecord.msg_date <= end_date,
                    MessageRecord.is_deleted == False
                )
            )
            .group_by(MessageRecord.source_group, GroupConfig.group_name)
            .order_by(func.count(MessageRecord.id).desc())
            .limit(limit)
        )
        
        result = await self.db.execute(query)
        rows = result.all()
        
        # 查询总消息数（用于计算占比）
        total_query = (
            select(func.count(MessageRecord.id))
            .where(
                and_(
                    MessageRecord.vin_code.isnot(None),
                    MessageRecord.msg_date >= start_date,
                    MessageRecord.msg_date <= end_date,
                    MessageRecord.is_deleted == False
                )
            )
        )
        total_result = await self.db.execute(total_query)
        total_count = total_result.scalar() or 0
        
        # 构建返回数据
        group_stats = []
        for row in rows:
            if row.source_group:  # 过滤掉空群名
                percentage = (row.message_count / total_count * 100) if total_count > 0 else 0
                group_stats.append({
                    'group_name': row.display_name or row.source_group,
                    'message_count': row.message_count,
                    'percentage': round(percentage, 2)
                })
        
        return {
            'total_vin_images': total_count,
            'period_days': days,
            'group_stats': group_stats
        }

    async def get_message_records(
        self,
        page: int = 1,
        page_size: int = 20,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        msg_type: Optional[str] = None,
        source_group: Optional[str] = None,
        inquirer: Optional[str] = None
    ):
        """获取消息记录"""
        skip = (page - 1) * page_size
        records, total = await message_crud.get_records(
            self.db,
            start_date=start_date,
            end_date=end_date,
            msg_type=msg_type,
            source_group=source_group,
            inquirer=inquirer,
            skip=skip,
            limit=page_size
        )

        return {
            "list": records,
            "total": total,
            "page": page,
            "page_size": page_size
        }
