import os

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



# 原始文件路径（假设有一个炸弹式的 JPG 文件 "bomb.jpg"）
file_path = 'bomb.jpg'

# 检查文件大小（打开前）
file_size_before = os.path.getsize(file_path)
print(f"打开前文件大小: {file_size_before / (1024 * 1024):.2f} MB")

# 打开文件并检查内存占用情况（打开后）
try:
    image = Image.open(file_path)
    image.load()  # 确保解码整个图像
    print("文件成功打开！")
    # 计算图像占用内存大小
    width, height = image.size
    memory_usage = width * height * 3  # 每个像素3字节 (RGB)
    print(f"打开后解码的内存占用: {memory_usage / (1024 * 1024):.2f} MB")
except Exception as e:
    print(f"打开文件时出错: {e}")
