import joblib

# 1. 加载模型
svm_model = joblib.load('svm_model.pkl')  # 加载保存的模型


# 2. 定义预测函数
def predict(input_features):
    prediction = svm_model.predict([input_features])
    if prediction[0] == 0:
        return "正常"
    else:
        return "非正常"


if __name__ == "__main__":
    # 3. 测试新数据
    new_data = [1480.1577216036608, 145055.45671715876]  # 替换为你要预测的新输入特征
    result = predict(new_data)
    print(f"输入特征 {new_data} 的预测结果是: {result}")
