"""
FastAPI 启动脚本
直接使用Python运行，无需uvicorn命令
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 使用Python内置的http.server和ASGI适配
import asyncio
from aiohttp import web

async def init_app():
    """初始化应用"""
    from app.main import app as fastapi_app
    
    async def handle(request):
        """处理请求"""
        from starlette.testclient import TestClient
        
        # 获取请求信息
        method = request.method
        path = request.path_qs
        headers = dict(request.headers)
        
        # 读取body
        body = await request.read()
        
        # 使用TestClient转发请求
        client = TestClient(fastapi_app)
        
        try:
            if body:
                response = client.request(
                    method=method,
                    url=path,
                    headers=headers,
                    content=body
                )
            else:
                response = client.request(
                    method=method,
                    url=path,
                    headers=headers
                )
            
            return web.Response(
                body=response.content,
                status=response.status_code,
                headers=dict(response.headers)
            )
        except Exception as e:
            return web.Response(
                text=f"Error: {str(e)}",
                status=500
            )
    
    app = web.Application()
    app.router.add_route('*', '/{path_info:.*}', handle)
    return app

async def main():
    """主函数"""
    app = await init_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8000)
    
    print("=" * 50)
    print("FastAPI Server Starting...")
    print("URL: http://0.0.0.0:8000")
    print("API Docs: http://0.0.0.0:8000/docs")
    print("=" * 50)
    
    await site.start()
    
    # 保持运行
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped")
