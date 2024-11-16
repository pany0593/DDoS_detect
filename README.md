- **使用环境**：

  - mininet中至少有一台switch

  - ryu运行

    ```
    sudo ryu-manager --verbose simple_switch.py ofctl_rest.py rest_topology.py
    ```

- **get_flow_rate.py**：调用ryu接口获取当前流量信息，一秒前后调用两次，得到一秒内包和比特数，除以时间得到packet_rate, byte_rate

-  **get_flows_rate.py**：调用get_flows_rate()构造训练数据集

  ```
  格式如：
  feature1,feature2,label
  1.0,2.0,1
  2.0,3.0,1
  3.0,3.0,0
  4.0,5.0,0
  1.5,2.5,1
  ```

-  **train_SVM.py**：训练SVM模型并保存为svm_model.pkl

-  **predict.py**：调用模型得到判断结果

-  **data.csv**：数据集，当前数据比较不真实，正常流量为1-2台主机ping，非正常流量为1-2台主机ping -f。等http服务和DDoS攻击功能实现后可以重新构建数据集训练

