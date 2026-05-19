import base64
import io
from typing import Union
from PIL import Image
from loguru import logger


class ImageProcessor:
    """图片处理器"""

    def __init__(self):
        self.max_size = 1920  # 最大边长
        self.quality = 85  # JPEG质量

    async def process(self, image_data: Union[bytes, str]) -> str:
        """
        处理图片

        Args:
            image_data: 图片二进制数据或base64字符串

        Returns:
            base64编码的图片
        """
        try:
            # 如果是base64字符串，先解码
            if isinstance(image_data, str):
                image_bytes = base64.b64decode(image_data)
            else:
                image_bytes = image_data

            # 打开图片
            image = Image.open(io.BytesIO(image_bytes))

            # 转换为RGB（处理RGBA等格式）
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # 调整大小
            image = self._resize_image(image)

            # 压缩并转为base64
            buffered = io.BytesIO()
            image.save(buffered, format='JPEG', quality=self.quality)
            img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

            return img_base64

        except Exception as e:
            logger.error(f"图片处理失败: {e}")
            # 如果处理失败，直接返回原始base64
            if isinstance(image_data, bytes):
                return base64.b64encode(image_data).decode('utf-8')
            return image_data

    def _resize_image(self, image: Image.Image) -> Image.Image:
        """调整图片大小"""
        width, height = image.size

        # 如果图片尺寸超过最大值，等比例缩小
        if width > self.max_size or height > self.max_size:
            ratio = min(self.max_size / width, self.max_size / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        return image
