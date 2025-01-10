import torch
import torch.nn as nn
import psutil
import os

# 获取当前进程的内存使用
def get_memory_usage():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return memory_info.rss / 1024 / 1024  # 以MB为单位

# 构造一个含有超大稀疏权重的模型
class LargeSparseModel(nn.Module):
    def __init__(self):
        super(LargeSparseModel, self).__init__()
        # 超大稀疏权重矩阵
        self.linear = nn.Linear(10 ** 4, 10 ** 4)
        with torch.no_grad():
            self.linear.weight.fill_(0)  # 填充为稀疏矩阵

    def forward(self, x):
        return self.linear(x)

# 保存模型
model = LargeSparseModel()
torch.save(model.state_dict(), "model_bomb.pt")
print("恶意模型已生成！")

# 打印加载前的内存使用
print(f"加载前内存使用: {get_memory_usage():.2f} MB")

# 加载模型
loaded_model_state_dict = torch.load("model_bomb.pt")
print(f"加载模型完成。")

# 打印加载后的内存使用
print(f"加载后内存使用: {get_memory_usage():.2f} MB")
