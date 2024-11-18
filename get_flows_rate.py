import requests
import json
import time


def get_aggregate_flow(swtid):
    # 记得修改对应url 1为switch编号
    url = f"http://192.168.24.134:8080/stats/aggregateflow/{swtid}"
    try:
        # 发送 GET 请求
        response = requests.get(url)
        if response.status_code == 200:
            try:
                # 解析 JSON 数据
                data = response.json()
                # 提取 packet_count 和 byte_count
                if "1" in data and isinstance(data["1"], list) and len(data["1"]) > 0:
                    packet_count = data["1"][0].get("packet_count", 0)
                    byte_count = data["1"][0].get("byte_count", 0)
                    return packet_count, byte_count
                else:
                    print("返回的数据格式不符合预期：", data)
                    return None, None
            except json.JSONDecodeError:
                print("响应不是有效的 JSON 格式：", response.text)
                return None, None
        else:
            print(f"请求失败，状态码：{response.status_code}")
            return None, None
    except requests.RequestException as e:
        print(f"请求时发生错误：{e}")
        return None, None


def get_flows_rate(swtid):
    start_time = time.time()
    packet_count1, byte_count1 = get_aggregate_flow(swtid)
    time.sleep(1)
    packet_count2, byte_count2 = get_aggregate_flow(swtid)
    end_time = time.time()
    # 毫秒
    execution_time = (end_time - start_time)
    packet_rate = (packet_count2 - packet_count1) / execution_time
    byte_rate = (byte_count2 - byte_count1) / execution_time
    if packet_rate is not None and byte_rate is not None:
        print(f"packet_rate: {packet_rate}, byte_rate: {byte_rate}")
    else:
        print("get_flows_rate()未能获取有效数据")
    if packet_rate >= 0 and byte_rate >= 0:
        return packet_rate, byte_rate
    else:
        return None, None


if __name__ == "__main__":
    get_flows_rate(1)
