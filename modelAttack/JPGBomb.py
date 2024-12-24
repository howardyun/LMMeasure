from PIL import Image
import numpy as np

# 创建一个非常大的图像
width, height = 1, 1
image = Image.new('RGB', (width, height), (255, 255, 255))

# 将图像数据填充为一个巨大数组
pixels = np.full((width * 10000, height * 10000, 3), 255, dtype=np.uint8)

# 创建一个大的JPG炸弹
large_image = Image.fromarray(pixels)
large_image.save('bomb.jpg', 'JPEG', quality=95)
