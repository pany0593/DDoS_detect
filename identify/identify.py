import requests
import json


def get_highest_packet_rate_in_port(swtid):
    """
    获取指定交换机编号中包率最高的项的 in_port。

    参数:
        swtid (int): 交换机编号，用于动态生成 URL。

    返回:
        int: 包率最高的项的 in_port。如果未找到有效数据，返回 None。
    """
    url = f"http://192.168.24.134:8080/stats/flow/{swtid}"
    try:
        # 发送 GET 请求
        response = requests.get(url)
        if response.status_code == 200:
            try:
                # 解析 JSON 数据
                data = response.json()
                highest_rate = 0
                in_port_with_highest_rate = None

                # 遍历流表数据
                for key, flows in data.items():
                    if isinstance(flows, list):
                        for flow in flows:
                            # 确保必要的字段存在
                            packet_count = flow.get("packet_count")
                            duration_sec = flow.get("duration_sec")
                            match = flow.get("match", {})
                            in_port = match.get("in_port")

                            if packet_count is not None and duration_sec is not None and duration_sec > 0 and in_port is not None:
                                # 计算包率
                                packet_rate = packet_count / duration_sec
                                # 更新最高包率和对应 in_port
                                if packet_rate > highest_rate:
                                    highest_rate = packet_rate
                                    in_port_with_highest_rate = in_port

                if in_port_with_highest_rate is not None:
                    return in_port_with_highest_rate
                else:
                    print("未找到有效的流表项。")
                    return None
            except json.JSONDecodeError:
                print("响应不是有效的 JSON 格式：", response.text)
                return None
        else:
            print(f"请求失败，状态码：{response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"请求时发生错误：{e}")
        return None


if __name__ == "__main__":
    # 示例调用
    swtid = 1  # 交换机编号
    in_port = get_highest_packet_rate_in_port(swtid)
    if in_port is not None:
        print(f"包率最高的项的 in_port 为: {in_port}")
    else:
        print("未能获取有效的包率信息。")
