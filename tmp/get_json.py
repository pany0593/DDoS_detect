from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

previous_packet_counts = {}


def get_output_and_in_ports(swtid):
    """
    获取指定交换机编号中每一项的 OUTPUT 值和 in_port 值。
    仅返回 packet_count 比上一次结果有增加的项。

    参数:
        swtid (int): 交换机编号，用于动态生成 URL。

    返回:
        list: 包含每一项的 (in_port, OUTPUT) 元组列表。如果未找到有效数据，返回空列表。
    """
    global previous_packet_counts
    url = f"http://192.168.24.134:8080/stats/flow/{swtid}"
    try:
        # 发送 GET 请求
        response = requests.get(url)
        if response.status_code == 200:
            try:
                # 解析 JSON 数据
                data = response.json()
                results = []

                # 用于记录本次请求的 packet_count
                current_packet_counts = {}

                # 遍历流表数据
                for key, flows in data.items():
                    if isinstance(flows, list):
                        for flow in flows:
                            # 确保必要的字段存在
                            match = flow.get("match", {})
                            actions = flow.get("actions", [])
                            in_port = match.get("in_port")
                            packet_count = flow.get("packet_count", 0)

                            # 提取 OUTPUT 值
                            output_value = None
                            for action in actions:
                                if isinstance(action, str) and action.startswith("OUTPUT:"):
                                    output_value = action.split(":")[1]
                                    break

                            # 如果 in_port 和 OUTPUT 都有效，且 packet_count 有效，则检查是否增加
                            if in_port is not None and output_value is not None:
                                # 当前项的唯一标识符
                                flow_id = f"{in_port}-{output_value}"
                                current_packet_counts[flow_id] = packet_count

                                # 如果是新项或 packet_count 增加
                                if flow_id not in previous_packet_counts or packet_count > previous_packet_counts[
                                    flow_id]:
                                    results.append({"in_port": in_port, "output": output_value})

                # 更新全局的 previous_packet_counts
                previous_packet_counts = current_packet_counts

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


def construct_full_paths():
    """
    根据两组流表数据构造完整路径。

    - 路径必须以主机发起，并以主机结束；
    - 每条路径最少两条记录，最多三条记录；
    - 匹配第一组流表的 OUTPUT 为 4 时，在第二组中寻找连接点。

    参数:
        json1 (dict): 第一组流表数据，包含 'data' 键。
        json2 (dict): 第二组流表数据，包含 'data' 键。

    返回:
        list: 包含多条完整路径，每条路径由 [{ src: str, dst: str }, ...] 构成。
    """
    # 定义端口到设备的映射
    mapping1 = {1: "h1", 2: "h2", 3: "h3", 4: "s2"}
    mapping2 = {1: "h4", 2: "h5", 3: "h6", 4: "s1"}

    # 提取数据
    flows1 = get_output_and_in_ports(1)  # 第一组数据
    flows2 = get_output_and_in_ports(2)  # 第二组数据
    # flows1 = json1.get("data", [])
    # flows2 = json2.get("data", [])

    # 用于标记第二组 JSON 中已经匹配过的条目
    matched_in_json2 = set()

    # 构造完整路径
    full_paths = []

    for flow1 in flows1:
        in_port = flow1.get("in_port")
        output = int(flow1.get("output", 0))  # 转换 output 为整数

        # 跳过非主机起始的条目
        if in_port not in mapping1 or not mapping1[in_port].startswith("h"):
            continue

        # 第一段：主机到交换机或其他主机
        first_link = {"src": mapping1[in_port], "dst": mapping1[output]}

        # 检查是否需要跨设备（output 为 4 时）
        if output == 4:
            for idx, flow2 in enumerate(flows2):
                if idx in matched_in_json2:  # 跳过已匹配的条目
                    continue

                in_port2 = flow2.get("in_port")
                output2 = int(flow2.get("output", 0))

                if in_port2 == 4:
                    # 第二段：交换机之间的连接
                    second_link = {"src": "s2", "dst": "s1"}

                    # 第三段：交换机到目标主机
                    third_link = {"src": mapping2[in_port2], "dst": mapping2[output2]} if output2 in mapping2 else None

                    # 构造完整路径
                    path = [first_link, second_link]
                    if third_link:
                        path.append(third_link)

                    full_paths.append(path)
                    matched_in_json2.add(idx)  # 标记此条目已匹配
                    break
        else:
            # 仅主机到交换机或主机的路径
            full_paths.append([first_link])

    return full_paths


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
        return jsonify({"data": "No new traffic detected"}), 200


if __name__ == "__main__":
    # 启动 Flask 应用
    app.run(host="0.0.0.0", port=6000)


# if __name__ == "__main__":
#     print(f"{get_output_and_in_ports(1)}")
