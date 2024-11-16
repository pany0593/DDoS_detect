import pandas as pd
from sklearn.svm import SVC
import joblib

data = pd.read_csv('data.csv')
X = data[['feature1', 'feature2']].values  # 特征
y = data['label'].values  # 标签

# 2. 创建并训练 SVM 模型
svm_model = SVC(kernel='linear', probability=True)
svm_model.fit(X, y)

# 3. 保存模型
joblib.dump(svm_model, 'svm_model.pkl')  # 将模型保存为 'svm_model.pkl'
print("模型已保存为 'svm_model.pkl'")
