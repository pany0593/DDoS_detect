#!/usr/bin/python3
import os
import random
# 可用的命令列表
start_commands = [
    "curl http://192.168.0.103:5000/start_hping",
    "curl http://192.168.0.105:5000/start_hping",
    "curl http://192.168.0.106:5000/start_hping",
]

def send_request():
    while True:
        print("Enter 1/2/3 to start hping3, 0 to stop hping3, or 'exit' to quit:")
        user_input = input("Your choice: ").strip()

        if user_input.isdigit() and int(user_input) > 0:
            # 随机执行对应数目的 start_hping 命令
            count = int(user_input)
            if count > len(start_commands):
                count = len(start_commands)
            selected_commands = random.sample(start_commands, count)
            for command in selected_commands:
                os.system(command)
        elif user_input == "0":
            # 发送 DELETE 请求到 /stop_hping
            os.system("curl -X DELETE http://192.168.0.103:5000/stop_hping")
            os.system("curl -X DELETE http://192.168.0.105:5000/stop_hping")
            os.system("curl -X DELETE http://192.168.0.106:5000/stop_hping")
        elif user_input.lower() == "exit":
            print("Exiting...")
            break
        else:
            print("Invalid input. Please enter '1', '0', or 'exit'.")


if __name__ == "__main__":
    send_request()
