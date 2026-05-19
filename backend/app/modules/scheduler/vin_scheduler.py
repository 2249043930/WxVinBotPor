from typing import Dict, Any, Optional
from loguru import logger
import httpx
from app.config import settings
from app.db.session import async_session
from app.crud.vin_info import vin_info_crud


class VinScheduler:
    """VIN查询调度器 - 优先从数据库查询，其次调用极速数据API"""

    def __init__(self):
        self.api_key = None  # 从配置获取
        self.base_url = "https://api.jisuapi.com/vin/query"

    async def query(self, vin_code: str) -> Optional[Dict[str, Any]]:
        """
        查询VIN信息

        查询优先级：
        1. 本地数据库缓存（优先）
        2. 极速数据API（外部接口）

        Args:
            vin_code: 17位VIN码

        Returns:
            VIN信息字典或None
        """
        # 1. 查询本地数据库（优先）
        local_result = await self._query_local(vin_code)
        if local_result:
            logger.info(f"从本地数据库找到VIN: {vin_code}")
            return local_result

        # 2. 查询极速数据API
        external_result = await self._query_jisu_api(vin_code)
        if external_result:
            # 缓存到数据库
            await self._cache_vin_info(vin_code, external_result)
            return external_result

        return None

    async def _query_local(self, vin_code: str) -> Optional[Dict[str, Any]]:
        """从本地数据库查询VIN信息"""
        try:
            async with async_session() as db:
                vin_info = await vin_info_crud.get_by_vin(db, vin_code=vin_code)
                if vin_info:
                    logger.info(f"本地数据库命中VIN: {vin_code}, 查询次数: {vin_info.query_count}")
                    return vin_info.to_dict()
                return None
        except Exception as e:
            logger.error(f"本地数据库查询VIN失败: {e}")
            return None

    async def _query_jisu_api(self, vin_code: str) -> Optional[Dict[str, Any]]:
        """查询极速数据API

        接口文档：https://api.jisuapi.com/vin/query
        错误码：
        - 101: APPKEY为空或不存在
        - 102: APPKEY已过期
        - 103: APPKEY无请求此数据权限
        - 104: 请求超过次数限制
        - 105: IP被禁止
        - 106: IP请求超过限制
        - 107: 接口维护中
        - 108: 接口已停用
        - 201: VIN为空
        - 202: VIN不正确
        - 210: 没有信息
        """
        if not self.api_key:
            self.api_key = settings.VIN_API_KEY

        if not vin_code:
            logger.error("错误：VIN码不能为空（错误码：201）")
            return None

        payload = {
            "appkey": self.api_key,
            "vin": vin_code.strip().upper()
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    data=payload,
                    timeout=10,
                    headers={
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'User-Agent': 'Mozilla/5.0 (compatible; VinQuery/1.0)'
                    }
                )
                response.raise_for_status()
                result = response.json()

                status = result.get("status")

                # 成功
                if status == 0:
                    data = result.get("result", {})
                    return self._format_vehicle_data(data)

                # 处理错误码
                error_codes = {
                    "101": "APPKEY为空或不存在",
                    "102": "APPKEY已过期",
                    "103": "APPKEY无请求此数据权限",
                    "104": "请求超过次数限制",
                    "105": "IP被禁止",
                    "106": "IP请求超过限制",
                    "107": "接口维护中",
                    "108": "接口已停用",
                    "201": "VIN为空",
                    "202": "VIN不正确",
                    "210": "没有信息"
                }

                error_msg = error_codes.get(str(status), f"未知错误: {status}")
                logger.error(f"极速数据API错误 [{status}]: {error_msg}")
                return None

        except httpx.TimeoutException:
            logger.error("请求超时，请检查网络连接")
            return None
        except httpx.HTTPError as e:
            logger.error(f"网络请求失败: {e}")
            return None
        except Exception as e:
            logger.error(f"查询极速数据API失败: {e}")
            return None

    def _format_vehicle_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """格式化车辆数据"""
        # 打印原始数据用于调试
        logger.debug(f"极速数据API返回的原始数据: {data}")
        
        # 机油相关字段的默认值（极速数据API可能不返回这些字段）
        # 根据车型和排量提供建议值
        displacement = data.get("displacement", "")
        
        # 根据排量提供默认机油建议
        default_volume = "4.0L"  # 默认机油用量
        default_viscosity = "5W-30"  # 默认粘度
        default_grade = "全合成"  # 默认等级
        default_level = "SN"  # 默认级别
        
        return {
            "vin": data.get("vin", ""),
            "manufacturer": data.get("manufacturer", ""),
            "brand": data.get("brand", ""),
            "model_info": data.get("name", ""),
            "typename": data.get("typename", ""),
            "displacement": displacement,
            "enginemodel": data.get("enginemodel", ""),
            "sizetype": data.get("sizetype", ""),
            "geartype": data.get("geartype", ""),
            "fronttiresize": data.get("fronttiresize", ""),
            "reartiresize": data.get("reartiresize", ""),
            "volume": data.get("volume") or default_volume,
            "viscosity": data.get("viscosity") or default_viscosity,
            "grade": data.get("grade") or default_grade,
            "level": data.get("level") or default_level,
            "source": "jisu_api"
        }

    async def _cache_vin_info(self, vin_code: str, info: Dict[str, Any]):
        """缓存VIN信息到数据库"""
        try:
            async with async_session() as db:
                await vin_info_crud.create_or_update(db, vin_data=info)
                logger.info(f"VIN信息已缓存到数据库: {vin_code}")
        except Exception as e:
            logger.error(f"缓存VIN信息失败: {e}")
