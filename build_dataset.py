import get_flows_rate
import csv


# 生成数据并写入 CSV
def generate_csv(filename, num_rows):
    # 使用 'a' 模式打开文件，以便追加数据
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)

        # 检查文件是否为空（即是否已有表头）
        file.seek(0, 2)  # 将文件指针移动到文件末尾
        if file.tell() == 0:  # 如果文件为空，写入表头
            writer.writerow(['feature1', 'feature2', 'label'])

        # 写入数据行
        for _ in range(num_rows):
            feature1, feature2 = get_flows_rate.get_flows_rate()
            writer.writerow([feature1, feature2, 1])  # label 始终为 0


if __name__ == "__main__":
    # 生成一个包含 5 行数据的 CSV 文件
    generate_csv('data.csv', 10)
    print("CSV 文件已生成：data.csv")
