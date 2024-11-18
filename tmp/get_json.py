from flask import Flask, request, jsonify, Response, json
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
    # 定义端口到设备的映射
    mapping1 = {1: "h1", 2: "h2", 3: "h3", 4: "s2"}
    mapping2 = {1: "h4", 2: "h5", 3: "h6", 4: "s1"}

    # 提取数据
    flows1 = get_output_and_in_ports(1)  # 第一组数据
    flows2 = get_output_and_in_ports(2)  # 第二组数据

    # 替换 flows1 中的数字为对应设备字符串，且修改字段名
    for flow in flows1:
        flow['src'] = mapping1.get(flow['in_port'], flow['in_port'])  # 修改为 src
        flow['dst'] = mapping1.get(int(flow['output']), flow['output'])  # 修改为 dst

        # 删除旧的 'in_port' 和 'output' 字段
        del flow['in_port']
        del flow['output']

    # 替换 flows2 中的数字为对应设备字符串，且修改字段名
    for flow in flows2:
        flow['src'] = mapping2.get(flow['in_port'], flow['in_port'])  # 修改为 src
        flow['dst'] = mapping2.get(int(flow['output']), flow['output'])  # 修改为 dst

        # 删除旧的 'in_port' 和 'output' 字段
        del flow['in_port']
        del flow['output']

    # 删除完全相同的条目
    unique_flows1 = []
    for flow in flows1:
        if flow not in unique_flows1:
            unique_flows1.append(flow)

    unique_flows2 = []
    for flow in flows2:
        if flow not in unique_flows2:
            unique_flows2.append(flow)

    paths = []  # 用于存储整理后的路径

    # 1. 对于 unique_flows1 和 unique_flows2 中，src 和 dst 都是以 'h' 开头的条目，直接加入 paths
    for flow in unique_flows1:
        if flow['src'].startswith('h') and flow['dst'].startswith('h'):
            paths.append([flow])

    # 2. 对于 unique_flows1 中，dst 为 's2' 的条目，去 unique_flows2 中寻找一条 src 为 's1' 的条目
    #    将他们用 [] 包裹后加入 paths，已匹配的条目不能再被匹配
    matched_in_flows2 = set()  # 用于标记 unique_flows2 中已经匹配过的条目

    for flow1 in unique_flows1:
        if flow1['dst'] == 's2':
            for idx, flow2 in enumerate(unique_flows2):
                if idx not in matched_in_flows2 and flow2['src'] == 's1':
                    # 匹配并生成路径
                    path = [flow1, flow2]
                    # 确保路径的第一条是主机
                    if not path[0]['src'].startswith('h'):
                        path[0], path[1] = path[1], path[0]  # 调换顺序
                    paths.append(path)
                    matched_in_flows2.add(idx)
                    break  # 跳出第二组流的循环，确保每个条目只匹配一次

    # 3. 对于 unique_flows1 中，src 为 's2' 的条目，去 unique_flows2 中寻找一条 dst 为 's1' 的条目
    #    将他们用 [] 包裹后加入 paths，已匹配的条目不能再被匹配
    for flow1 in unique_flows1:
        if flow1['src'] == 's2':
            for idx, flow2 in enumerate(unique_flows2):
                if idx not in matched_in_flows2 and flow2['dst'] == 's1':
                    # 匹配并生成路径
                    path = [flow1, flow2]
                    # 确保路径的第一条是主机
                    if not path[0]['src'].startswith('h'):
                        path[0], path[1] = path[1], path[0]  # 调换顺序
                    paths.append(path)
                    matched_in_flows2.add(idx)
                    break  # 跳出第二组流的循环，确保每个条目只匹配一次

    modified_paths = []
    for path in paths:
        if len(path) == 1:
            # 1. 如果只有一条主机到主机的路径，检查 src 主机
            if path[0]['src'] in ['h1', 'h2', 'h3']:
                # 以 h1, h2, h3 为 src，改为通过 s1 的路径
                modified_paths.append([{'src': path[0]['src'], 'dst': 's1'}, {'src': 's1', 'dst': path[0]['dst']}])
            else:
                # 否则，改为通过 s2 的路径
                modified_paths.append([{'src': path[0]['src'], 'dst': 's2'}, {'src': 's2', 'dst': path[0]['dst']}])

        elif len(path) == 2:
            # 2. 如果有两条条目，在中间添加一条经过 s1 或 s2 的路径
            if path[0]['src'] in ['h1', 'h2', 'h3']:
                # 插入通过 s1 的路径
                modified_paths.append([{'src': path[0]['src'], 'dst': 's1'}, {'src': 's1', 'dst': 's2'},
                                       {'src': 's2', 'dst': path[1]['dst']}])
            else:
                # 否则，插入通过 s2 的路径
                modified_paths.append([{'src': path[0]['src'], 'dst': 's2'}, {'src': 's2', 'dst': 's1'},
                                       {'src': 's1', 'dst': path[1]['dst']}])

    return modified_paths


@app.route('/get_json', methods=['GET'])
def handle_request():
    """
    处理 /get_json 请求，返回完整路径的结果。

    返回：
        JSON: 构造的路径数据。
    """
    try:
        # 调用 construct_full_paths_via_api 获取路径结果
        paths = construct_full_paths()
        print(f"{construct_full_paths()}")

        if paths:
            return Response(json.dumps(paths, sort_keys=False), mimetype='application/json', status=200)
        else:
            return jsonify({"message": "No valid paths detected"}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


if __name__ == "__main__":
    # 启动 Flask 应用
    app.run(host="0.0.0.0", port=6000)


# if __name__ == "__main__":
#     print(f"{construct_full_paths()}")
