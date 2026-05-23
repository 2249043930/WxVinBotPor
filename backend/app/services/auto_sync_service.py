"""
智能同步服务
实现一键智能同步供应商-车型绑定功能
"""

from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from app.crud.group_config import group_config_crud
from app.crud.group_member import group_member_crud
from app.crud.group import group_crud
from app.models.group_config import GroupConfig, GroupModelSupplier
from app.services.group_service import GroupService


class AutoSyncService:
    """智能同步服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def sync_supplier_model_bindings(
        self,
        source_group_id: Optional[str] = None,
        target_group_ids: Optional[List[str]] = None
    ) -> Dict:
        """智能同步供应商-车型绑定
        
        核心逻辑：
        1. 综合所有已配置群的供应商-车型绑定（去重）
        2. 获取所有供应商的wxid
        3. 扫描目标群的成员列表
        4. 如果发现目标群也有相同的供应商wxid，自动创建相同的绑定
        
        Args:
            source_group_id: 源群ID（可选，不传则自动综合所有已配置群）
            target_group_ids: 目标群ID列表（可选，不传则同步所有群）
            
        Returns:
            Dict: 同步结果
        """
        logger.info(f"开始智能同步: source_group_id={source_group_id}")
        
        # 1. 获取所有绑定（综合所有已配置群或指定源群）
        if source_group_id:
            # 指定了源群，只使用该群的绑定
            source_config = await group_config_crud.get_by_group_id(
                self.db, source_group_id, load_relations=True
            )
            
            if not source_config:
                raise ValueError("源群配置不存在")
            
            if not source_config.model_suppliers:
                raise ValueError("源群没有配置车型-供应商绑定")
            
            source_bindings = []
            for source_ms in source_config.model_suppliers:
                source_bindings.append({
                    'car_model_id': source_ms.car_model_id,
                    'supplier_id': source_ms.supplier_id,
                    'supplier_wxid': source_ms.supplier.wxid if source_ms.supplier else None,
                    'supplier_name': source_ms.supplier.name if source_ms.supplier else "未知",
                    'car_model_name': source_ms.car_model.name if source_ms.car_model else "未知"
                })
            
            logger.info(f"使用指定源群，共有 {len(source_bindings)} 个绑定")
        else:
            # 未指定源群，综合所有已配置群的绑定
            source_bindings = await self._get_all_bindings_from_configured_groups()
            
            if not source_bindings:
                raise ValueError("系统中没有配置任何车型-供应商绑定")
            
            logger.info(f"综合所有已配置群，共有 {len(source_bindings)} 个唯一绑定")
        
        # 2. 获取目标群列表（所有群）
        if not target_group_ids:
            all_groups = await group_crud.get_multi(self.db, skip=0, limit=1000)
            target_group_ids = [g.group_id for g in all_groups]
        
        # 不限制目标群数量，处理所有群聊
        original_count = len(target_group_ids)
        logger.info(f"总共需要处理 {original_count} 个目标群")
        
        # 4. 执行同步
        sync_results = []
        total_created = 0
        total_skipped = 0
        processed_count = 0
        member_sync_failures = 0
        
        # 详细跳过原因统计
        skip_reasons = {
            "no_supplier_wxid": 0,  # 供应商无wxid
            "binding_exists": 0,    # 绑定已存在
            "same_model_diff_supplier": 0,  # 同车型不同供应商
            "no_member": 0,         # 目标群无此供应商成员
            "member_sync_failed": 0,  # 成员同步失败
            "create_failed": 0      # 创建失败
        }
        
        for target_group_id in target_group_ids:
            processed_count += 1
            logger.info(f"处理第 {processed_count}/{len(target_group_ids)} 个群: {target_group_id}")
            
            # 同步目标群成员
            member_sync_result = await self._sync_group_members(target_group_id)
            member_sync_failed = not member_sync_result.get("success")
            if member_sync_failed:
                logger.warning(f"群成员同步失败 {target_group_id}: {member_sync_result.get('message')}")
                member_sync_failures += 1
                skip_reasons["member_sync_failed"] += 1
                # 继续处理，但会因为没有成员而跳过所有绑定
            
            # 执行绑定同步
            result = await self._sync_bindings_to_target(
                source_bindings,
                target_group_id,
                member_sync_failed
            )
            
            # 统计跳过原因
            for binding in result.get("skipped_bindings", []):
                reason = binding.get("reason", "")
                if "供应商无wxid" in reason:
                    skip_reasons["no_supplier_wxid"] += 1
                elif "绑定已存在" in reason and "数据库约束" not in reason:
                    skip_reasons["binding_exists"] += 1
                elif "目标群已有此车型绑定" in reason or "数据库约束" in reason:
                    skip_reasons["same_model_diff_supplier"] += 1
                elif "目标群无此供应商成员" in reason:
                    skip_reasons["no_member"] += 1
                elif "创建失败" in reason:
                    skip_reasons["create_failed"] += 1
            
            # 只记录有创建的群
            if result["created"] > 0:
                sync_results.append(result)
            total_created += result["created"]
            total_skipped += result["skipped"]
        
        logger.info(f"智能同步完成: 创建={total_created}, 跳过={total_skipped}, 成员同步失败={member_sync_failures}")
        logger.info(f"跳过原因统计: {skip_reasons}")
        
        # 构建返回结果
        result_data = {
            "success": True,
            "total_target_groups": original_count,
            "processed_groups": processed_count,
            "member_sync_failures": member_sync_failures,
            "limited": False,
            "total_created": total_created,
            "total_skipped": total_skipped,
            "skip_reasons": skip_reasons,
            "details": sync_results
        }
        
        # 如果指定了源群，显示源群信息；否则显示综合模式
        if source_group_id:
            result_data["source_group"] = source_group_id
            result_data["source_group_name"] = source_config.group_name
        else:
            result_data["source_group"] = "all"
            result_data["source_group_name"] = "综合所有已配置群"
        
        return result_data

    async def _get_all_bindings_from_configured_groups(self) -> List[Dict]:
        """获取所有已配置群的绑定关系（去重）
        
        遍历所有已配置群聊，收集所有唯一的(车型, 供应商)绑定组合
        
        Returns:
            List[Dict]: 去重后的绑定列表
        """
        logger.info("开始收集所有已配置群的绑定关系")
        
        # 直接查询 group_model_suppliers 表，避免懒加载问题
        from app.models.group_config import GroupModelSupplier, GroupConfig
        from app.models.car_model import CarModel, Supplier
        
        # 使用 join 一次性查询所有需要的数据
        result = await self.db.execute(
            select(
                GroupModelSupplier.car_model_id,
                GroupModelSupplier.supplier_id,
                Supplier.wxid.label('supplier_wxid'),
                Supplier.name.label('supplier_name'),
                CarModel.name.label('car_model_name'),
                GroupConfig.group_name,
                GroupConfig.group_id
            )
            .join(Supplier, GroupModelSupplier.supplier_id == Supplier.id)
            .join(CarModel, GroupModelSupplier.car_model_id == CarModel.id)
            .join(GroupConfig, GroupModelSupplier.group_config_id == GroupConfig.id)
            .where(GroupModelSupplier.is_deleted == False)
            .where(GroupConfig.is_deleted == False)
        )
        
        all_bindings = result.all()
        logger.info(f"从数据库查询到 {len(all_bindings)} 个绑定关系")
        
        # 使用集合去重：(car_model_id, supplier_id) -> binding_info
        unique_bindings = {}
        
        for row in all_bindings:
            key = (row.car_model_id, row.supplier_id)
            group_name = row.group_name or row.group_id
            
            if key not in unique_bindings:
                unique_bindings[key] = {
                    'car_model_id': row.car_model_id,
                    'supplier_id': row.supplier_id,
                    'supplier_wxid': row.supplier_wxid,
                    'supplier_name': row.supplier_name or "未知",
                    'car_model_name': row.car_model_name or "未知",
                    'source_groups': [group_name]
                }
            else:
                # 记录该绑定还存在于其他群
                if group_name not in unique_bindings[key]['source_groups']:
                    unique_bindings[key]['source_groups'].append(group_name)
        
        bindings_list = list(unique_bindings.values())
        logger.info(f"去重后找到 {len(bindings_list)} 个唯一的绑定关系")
        
        # 记录每个绑定的来源群
        for binding in bindings_list:
            logger.info(f"绑定: {binding['car_model_name']} - {binding['supplier_name']}, "
                       f"来源群: {len(binding['source_groups'])} 个")
        
        return bindings_list

    async def _sync_group_members(self, group_id: str) -> Dict:
        """同步群成员到数据库
        
        Args:
            group_id: 群ID
            
        Returns:
            Dict: 同步结果
        """
        try:
            # 从千寻API获取群成员
            group_service = GroupService(self.db)
            members = await group_service.get_members(group_id)
            
            if not members:
                logger.warning(f"获取群成员为空: {group_id}")
                return {"success": False, "message": "获取群成员失败或为空"}
            
            # 同步到数据库
            result = await group_member_crud.sync_members(self.db, group_id, members)
            logger.info(f"同步群成员完成: {group_id}, {result}")
            
            return {"success": True, **result}
            
        except Exception as e:
            logger.error(f"同步群成员失败: {group_id}, {e}")
            return {"success": False, "message": str(e)}

    async def _sync_bindings_to_target(
        self,
        source_bindings: List[Dict],
        target_group_id: str,
        member_sync_failed: bool = False
    ) -> Dict:
        """将源群的绑定同步到目标群
        
        Args:
            source_bindings: 源群绑定数据列表
            target_group_id: 目标群ID
            
        Returns:
            Dict: 同步结果
        """
        created_bindings = []
        skipped_bindings = []
        
        # 获取目标群的现有配置（如果有）
        target_config = await group_config_crud.get_by_group_id(
            self.db, target_group_id, load_relations=True
        )
        
        # 获取目标群的成员
        target_members = await group_member_crud.get_by_group_id(self.db, target_group_id)
        target_member_wxids = {m.wxid for m in target_members}
        
        logger.info(f"目标群 {target_group_id} 成员数: {len(target_member_wxids)}")
        
        # 如果成员为空，记录警告
        if not target_member_wxids:
            logger.warning(f"目标群 {target_group_id} 没有成员数据，请检查群成员同步功能")
        
        # 获取目标群已有的绑定（避免重复创建）
        # 注意：数据库唯一约束是 (group_config_id, car_model_id)
        # 同一个车型只能绑定一个供应商
        existing_bindings = set()  # (car_model_id, supplier_id)
        existing_car_models = set()  # car_model_id only
        if target_config and target_config.model_suppliers:
            logger.info(f"目标群已有 {len(target_config.model_suppliers)} 个绑定")
            for ms in target_config.model_suppliers:
                existing_bindings.add((ms.car_model_id, ms.supplier_id))
                existing_car_models.add(ms.car_model_id)
                logger.info(f"  已有绑定: car_model_id={ms.car_model_id}, supplier_id={ms.supplier_id}")
        else:
            logger.info(f"目标群没有现有绑定")
        
        logger.info(f"existing_bindings: {existing_bindings}")
        logger.info(f"existing_car_models: {existing_car_models}")
        
        # 获取目标群信息（提前获取，避免后续使用时报错）
        target_group = await group_crud.get_by_group_id(self.db, target_group_id)
        target_group_name = target_group.group_name if target_group else target_group_id
        
        # 如果成员同步失败，跳过所有绑定
        if member_sync_failed:
            for binding in source_bindings:
                skipped_bindings.append({
                    "car_model": binding['car_model_name'],
                    "supplier": binding['supplier_name'],
                    "reason": "成员同步失败"
                })
            return {
                "group_id": target_group_id,
                "group_name": target_group_name,
                "created": 0,
                "skipped": len(skipped_bindings),
                "created_bindings": created_bindings,
                "skipped_bindings": skipped_bindings
            }
        
        # 遍历源群的所有绑定
        for binding in source_bindings:
            supplier_wxid = binding['supplier_wxid']
            car_model_id = binding['car_model_id']
            supplier_id = binding['supplier_id']
            supplier_name = binding['supplier_name']
            car_model_name = binding['car_model_name']
            
            logger.info(f"检查绑定: 车型={car_model_name}, 供应商={supplier_name}, wxid={supplier_wxid}")
            
            if not supplier_wxid:
                logger.warning(f"供应商 {supplier_name} 没有 wxid，跳过")
                skipped_bindings.append({
                    "car_model": car_model_name,
                    "supplier": supplier_name,
                    "reason": "供应商无wxid"
                })
                continue
            
            # 检查目标群是否已有此车型绑定（数据库约束：同一车型只能绑定一个供应商）
            if car_model_id in existing_car_models:
                logger.info(f"车型 {car_model_name} 已在目标群绑定其他供应商，跳过")
                skipped_bindings.append({
                    "car_model": car_model_name,
                    "supplier": supplier_name,
                    "reason": "目标群已有此车型绑定"
                })
                continue
            
            # 检查目标群是否已有完全相同的绑定
            if (car_model_id, supplier_id) in existing_bindings:
                logger.info(f"绑定已存在: {car_model_name} - {supplier_name}")
                skipped_bindings.append({
                    "car_model": car_model_name,
                    "supplier": supplier_name,
                    "reason": "绑定已存在"
                })
                continue
            
            # 检查目标群是否有此供应商成员
            if not target_member_wxids:
                skipped_bindings.append({
                    "car_model": car_model_name,
                    "supplier": supplier_name,
                    "reason": "目标群成员数据为空"
                })
                continue
            
            logger.info(f"检查供应商 wxid {supplier_wxid} 是否在目标群中: {supplier_wxid in target_member_wxids}")
            
            if supplier_wxid not in target_member_wxids:
                skipped_bindings.append({
                    "car_model": car_model_name,
                    "supplier": supplier_name,
                    "reason": "目标群无此供应商成员"
                })
                continue
            
            # 创建绑定
            try:
                if not target_config:
                    # 目标群没有配置，先创建配置
                    target_group = await group_crud.get_by_group_id(self.db, target_group_id)
                    target_config = await group_config_crud.create_with_models(
                        self.db,
                        group_id=target_group_id,
                        group_name=target_group.group_name if target_group else None,
                        model_suppliers=[{"car_model_id": car_model_id, "supplier_id": supplier_id}]
                    )
                    # 更新 existing_bindings 和 existing_car_models，防止后续重复
                    existing_bindings.add((car_model_id, supplier_id))
                    existing_car_models.add(car_model_id)
                else:
                    # 添加绑定到现有配置
                    new_binding = GroupModelSupplier(
                        group_config_id=target_config.id,
                        car_model_id=car_model_id,
                        supplier_id=supplier_id
                    )
                    self.db.add(new_binding)
                    await self.db.commit()
                    # 重新查询 target_config 以避免懒加载问题
                    target_config = await group_config_crud.get_by_group_id(
                        self.db, target_group_id, load_relations=True
                    )
                    # 更新 existing_bindings 和 existing_car_models
                    existing_bindings.add((car_model_id, supplier_id))
                    existing_car_models.add(car_model_id)
                
                created_bindings.append({
                    "car_model": car_model_name,
                    "supplier": supplier_name
                })
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"创建绑定失败: {error_msg}")
                
                # 检查是否是重复键错误
                if "Duplicate entry" in error_msg or "unique_group_model" in error_msg:
                    skipped_bindings.append({
                        "car_model": car_model_name,
                        "supplier": supplier_name,
                        "reason": "绑定已存在(数据库约束)"
                    })
                    # 回滚事务
                    await self.db.rollback()
                else:
                    skipped_bindings.append({
                        "car_model": car_model_name,
                        "supplier": supplier_name,
                        "reason": f"创建失败: {error_msg}"
                    })
                    # 回滚事务
                    await self.db.rollback()
        
        return {
            "group_id": target_group_id,
            "group_name": target_group_name,
            "created": len(created_bindings),
            "skipped": len(skipped_bindings),
            "created_bindings": created_bindings,
            "skipped_bindings": skipped_bindings
        }

    async def preview_sync(
        self,
        source_group_id: str,
        target_group_ids: Optional[List[str]] = None
    ) -> Dict:
        """预览同步结果（不实际执行）
        
        Args:
            source_group_id: 源群ID
            target_group_ids: 目标群ID列表（可选）
            
        Returns:
            Dict: 预览结果
        """
        logger.info(f"预览智能同步: 源群={source_group_id}")
        
        # 获取源群配置
        source_config = await group_config_crud.get_by_group_id(
            self.db, source_group_id, load_relations=True
        )
        
        if not source_config:
            raise ValueError("源群配置不存在")
        
        if not source_config.model_suppliers:
            raise ValueError("源群没有配置车型-供应商绑定")
        
        # 获取目标群
        if not target_group_ids:
            all_groups = await group_crud.get_multi(self.db, skip=0, limit=1000)
            target_group_ids = [g.group_id for g in all_groups if g.group_id != source_group_id]
        
        # 预览每个目标群的同步结果
        preview_results = []
        total_would_create = 0
        member_sync_failures = 0
        
        for target_group_id in target_group_ids[:10]:  # 只预览前10个群
            # 同步成员（为了预览准确性）
            member_sync_result = await self._sync_group_members(target_group_id)
            if not member_sync_result.get("success"):
                member_sync_failures += 1
            
            # 计算会创建的绑定数量
            would_create = await self._preview_bindings(
                source_config, target_group_id
            )
            
            if would_create > 0:
                target_group = await group_crud.get_by_group_id(self.db, target_group_id)
                preview_results.append({
                    "group_id": target_group_id,
                    "group_name": target_group.group_name if target_group else target_group_id,
                    "would_create": would_create
                })
                total_would_create += would_create
        
        return {
            "success": True,
            "source_group": source_group_id,
            "source_group_name": source_config.group_name,
            "total_target_groups": len(target_group_ids),
            "preview_groups": len(preview_results),
            "member_sync_failures": member_sync_failures,
            "total_would_create": total_would_create,
            "details": preview_results
        }

    async def _preview_bindings(
        self,
        source_config: GroupConfig,
        target_group_id: str
    ) -> int:
        """预览会创建的绑定数量
        
        Args:
            source_config: 源群配置
            target_group_id: 目标群ID
            
        Returns:
            int: 会创建的绑定数量
        """
        would_create = 0
        
        # 获取目标群的现有绑定
        target_config = await group_config_crud.get_by_group_id(
            self.db, target_group_id, load_relations=True
        )
        
        existing_bindings = set()
        if target_config and target_config.model_suppliers:
            for ms in target_config.model_suppliers:
                existing_bindings.add((ms.car_model_id, ms.supplier_id))
        
        # 获取目标群成员
        target_members = await group_member_crud.get_by_group_id(self.db, target_group_id)
        target_member_wxids = {m.wxid for m in target_members}
        
        # 计算会创建的绑定
        for source_ms in source_config.model_suppliers:
            supplier_wxid = source_ms.supplier.wxid if source_ms.supplier else None
            car_model_id = source_ms.car_model_id
            supplier_id = source_ms.supplier_id
            
            if not supplier_wxid:
                continue
            
            # 检查是否已存在
            if (car_model_id, supplier_id) in existing_bindings:
                continue
            
            # 检查目标群是否有此供应商
            if supplier_wxid in target_member_wxids:
                would_create += 1
        
        return would_create
