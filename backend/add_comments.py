#!/usr/bin/env python3
"""
为所有模型添加中文注释的脚本
"""

import os
import re

# 模型文件路径
models_dir = "d:/Client Projects/WxVinBot Por/backend/app/models"

# 表注释映射
table_comments = {
    "users": "用户表 - 存储系统用户信息",
    "logs": "日志表 - 存储操作日志",
    "operation_logs": "操作日志表 - 存储详细操作记录",
    "accounts": "账号表 - 存储微信账号信息",
    "statistics": "统计表 - 存储VIN查询统计",
    "message_records": "消息记录表 - 存储群聊消息",
    "member_types": "成员类型表 - 存储供应商成员类型",
    "suppliers": "供应商表 - 存储供应商信息",
    "car_models": "车型表 - 存储车型配置信息",
    "car_model_supplier": "车型供应商关联表 - 车型与供应商多对多关系",
    "wechat_groups": "微信群表 - 存储群聊信息",
    "system_configs": "系统配置表 - 存储系统配置项",
    "api_configs": "接口配置表 - 存储API接口配置",
    "vin_info": "VIN信息表 - 存储车架号查询结果",
}

# 字段注释映射
field_comments = {
    # 通用字段
    "id": "主键ID",
    "created_at": "创建时间",
    "updated_at": "更新时间",
    "is_deleted": "是否删除：0-未删除，1-已删除",
    
    # User表
    "nickname": "用户昵称",
    "username": "登录账号",
    "password_hash": "密码哈希值",
    "phone": "手机号码",
    "email": "邮箱地址",
    "remark": "备注信息",
    "is_active": "是否启用：0-禁用，1-启用",
    "is_superuser": "是否超级管理员：0-否，1-是",
    "wx_id": "微信ID",
    "wx_group_name": "微信群聊名称及wxid",
    "group_member_wxid": "群成员wxid",
    
    # Log表
    "user_id": "用户ID",
    "action": "操作类型",
    "module": "操作模块",
    "description": "操作描述",
    "ip_address": "IP地址",
    "user_agent": "用户代理",
    "request_data": "请求数据",
    "response_data": "响应数据",
    "status": "操作状态：0-失败，1-成功",
    "error_message": "错误信息",
    
    # Account表
    "account_name": "账号名称",
    "wx_account": "微信号",
    "avatar": "头像URL",
    "is_online": "是否在线：0-离线，1-在线",
    "last_login": "最后登录时间",
    
    # Statistics表
    "date": "日期",
    "recognize_status": "识别状态",
    "vin_code": "车架号VIN",
    "car_model": "车型信息",
    "source_group": "来源群聊",
    "inquirer": "询价人",
    "quoter": "报价人",
    "is_quoted": "是否已报价：0-未报价，1-已报价",
    "quote_time": "报价时间",
    "supplier": "供应商",
    
    # MessageRecord表
    "group_id": "群ID",
    "group_name": "群名称",
    "sender_wxid": "发送者微信ID",
    "sender_nick": "发送者昵称",
    "msg_content": "消息内容",
    "msg_type": "消息类型：text-文本，image-图片，voice-语音，video-视频",
    "msg_time": "消息时间",
    "image_content": "图片内容Base64",
    
    # MemberType表
    "type_name": "类型名称",
    "type_code": "类型代码",
    "sort_order": "排序顺序",
    
    # Supplier表
    "supplier_name": "供应商名称",
    "supplier_code": "供应商代码",
    "contact_name": "联系人姓名",
    "contact_phone": "联系人电话",
    "contact_wx": "联系人微信",
    "address": "地址",
    "member_type_id": "成员类型ID",
    "category": "供应类别",
    "is_default": "是否默认：0-否，1-是",
    
    # CarModel表
    "name": "车型名称",
    "brand": "品牌",
    "series": "车系",
    "displacement": "排量",
    "year": "年份",
    "member_types": "适用成员类型",
    
    # WechatGroup表
    "member_count": "成员数量",
    "inquiry_notify": "询价通知：0-关闭，1-开启",
    "quote_notify": "报价通知：0-关闭，1-开启",
    "delivery_notify": "发货通知：0-关闭，1-开启",
    "deal_notify": "成交通知：0-关闭，1-开启",
    "work_start_time": "工作开始时间",
    "work_end_time": "工作结束时间",
    "notify_keywords": "通知关键词",
    
    # SystemConfig表
    "config_key": "配置键",
    "config_value": "配置值",
    "config_type": "配置类型",
    
    # ApiConfig表
    "config_type": "配置类型：llm-大模型，vin-VIN接口，db-数据库",
    "api_key": "API密钥",
    "api_base": "API基础地址",
    "api_secret": "API密钥",
    "model": "模型名称",
    "temperature": "温度参数",
    "max_tokens": "最大令牌数",
    "prompt_template": "提示词模板",
    "db_host": "数据库主机",
    "db_port": "数据库端口",
    "db_name": "数据库名称",
    "db_user": "数据库用户",
    "db_password": "数据库密码",
    "wx_id": "微信ID",
    "api_url": "API地址",
    "is_default": "是否默认：0-否，1-是",
    "description": "描述",
    "sort_order": "排序顺序",
    
    # VinInfo表
    "vin_code": "车架号VIN",
    "manufacturer": "厂商",
    "car_model": "车型名称",
    "series": "车系",
    "typename": "车辆类型",
    "enginemodel": "发动机型号",
    "sizetype": "车辆尺寸类型",
    "geartype": "变速箱类型",
    "fronttiresize": "前轮尺寸",
    "reartiresize": "后轮尺寸",
    "volume": "机油用量",
    "viscosity": "机油粘度",
    "grade": "机油等级",
    "level": "机油级别",
    "source": "数据来源",
    "query_count": "查询次数",
    "last_query_time": "最后查询时间",
}

def add_comments_to_file(filepath):
    """为单个文件添加注释"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    filename = os.path.basename(filepath)
    
    # 添加文件头注释
    if not content.startswith('"""'):
        model_name = filename.replace('.py', '')
        header = f'"""\n{model_name}模型模块\n定义{model_name}表结构\n"""\n\n'
        content = header + content
    
    # 为类添加表注释
    for table_name, comment in table_comments.items():
        # 查找 __tablename__ = "xxx" 并添加 __table_args__
        pattern = rf'(__tablename__\s*=\s*["\']{table_name}["\'])'
        if re.search(pattern, content) and '__table_args__' not in content:
            replacement = rf'\1\n    __table_args__ = {{"comment": "{comment}"}}'
            content = re.sub(pattern, replacement, content)
    
    # 为字段添加注释
    for field, comment in field_comments.items():
        # 匹配 Column 定义并添加 comment 参数
        # 匹配形如：field = Column(...) 但还没有 comment 的
        pattern = rf'({field}\s*=\s*Column\([^)]*?)(\))'
        
        def replacer(match):
            col_def = match.group(1)
            closing = match.group(2)
            # 如果已经有 comment，跳过
            if 'comment=' in col_def:
                return match.group(0)
            # 添加 comment
            return f'{col_def}, comment="{comment}"{closing}'
        
        content = re.sub(pattern, replacer, content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"已更新: {filename}")

# 处理所有模型文件
for filename in os.listdir(models_dir):
    if filename.endswith('.py') and filename not in ['__init__.py', 'base.py']:
        filepath = os.path.join(models_dir, filename)
        add_comments_to_file(filepath)

print("\n所有模型文件已添加中文注释！")
