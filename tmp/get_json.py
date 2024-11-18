from flask import Flask, request, jsonify
import requests

app = Flask(__name__)


def get_output_and_in_ports(swtid):
    """
    获取指定交换机编号中每一项的 OUTPUT 值和 in_port 值。

    参数:
        swtid (int): 交换机编号，用于动态生成 URL。

    返回:
        list: 包含每一项的 (in_port, OUTPUT) 元组列表。如果未找到有效数据，返回空列表。
    """
    url = f"http://192.168.24.134:8080/stats/flow/{swtid}"
    try:
        # 发送 GET 请求
        response = requests.get(url)
        if response.status_code == 200:
            try:
                # 解析 JSON 数据
                data = response.json()
                results = []

                # 遍历流表数据
                for key, flows in data.items():
                    if isinstance(flows, list):
                        for flow in flows:
                            # 确保必要的字段存在
                            match = flow.get("match", {})
                            actions = flow.get("actions", [])
                            in_port = match.get("in_port")

                            # 提取 OUTPUT 值
                            output_value = None
                            for action in actions:
                                if isinstance(action, str) and action.startswith("OUTPUT:"):
                                    output_value = action.split(":")[1]
                                    break

                            # 如果 in_port 和 OUTPUT 都有效，则加入结果
                            if in_port is not None and output_value is not None:
                                results.append({"in_port": in_port, "output": output_value})

                return results
            except Exception as e:
                print("解析响应时发生错误：", e)
                return []
        else:
            print(f"请求失败，状态码：{response.status_code}")
            return []
    except requests.RequestException as e:
        print(f"请求时发生错误：{e}")
        return []


@app.route('/get_json', methods=['GET'])
def handle_request():
    """
    处理 /get_json 请求，返回流表中 in_port 和 OUTPUT 值的结果。

    查询参数：
        swtid: 交换机编号。

    返回：
        JSON: 结果数据。
    """
    swtid = request.args.get('swtid', type=int)
    if swtid is None:
        return jsonify({"error": "Missing or invalid 'swtid' parameter"}), 400

    result = get_output_and_in_ports(swtid)
    if result:
        return jsonify({"data": result}), 200
    else:
        return jsonify({"error": "No valid data found"}), 404


if __name__ == "__main__":
    # 启动 Flask 应用
    app.run(host="0.0.0.0", port=6000)
