import joblib

from get_flows_rate import get_flows_rate

# 1. 加载模型
svm_model = joblib.load('svm_model.pkl')  # 加载保存的模型


# 2. 定义预测函数
def predict(swtid):
    packet_rate, byte_rate = get_flows_rate(swtid)
    input_features = [packet_rate, byte_rate]  # 替换为你要预测的特征
    prediction = svm_model.predict([input_features])
    if prediction[0] == 0:
        return "正常"
    else:
        return "非正常"


if __name__ == "__main__":
    print(f"当前{predict(2)}")
