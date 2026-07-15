import pandas as pd
import matplotlib.pyplot as plt

# ================= 檔案路徑設定 =================
# 請替換為您實際的 FIO log 檔名
IOPS_LOG_1 = "benchmark_log/FIO/_iops.1.log"
IOPS_LOG_2 = "benchmark_log/FIO/_iops.2.log"
IOPS_LOG_3 = "benchmark_log/FIO/_iops.3.log"

BW_LOG_1 = "benchmark_log/FIO/_bw.1.log"
BW_LOG_2 = "benchmark_log/FIO/_bw.2.log"
BW_LOG_3 = "benchmark_log/FIO/_bw.3.log" 

def process_fio_log(log_file, log_type):
    """讀取並解析單一 FIO log 檔案，自動處理單位轉換並去除極端值"""
    print(f"正在解析 {log_file} ...")
    try:
        # FIO log 格式: [時間(ms), 數值, 方向(0=R,1=W), 區塊大小(bytes)]
        df = pd.read_csv(log_file, header=None, usecols=range(4), 
                         names=['Time_ms', 'Value', 'DDIR', 'BlockSize'])
    except FileNotFoundError:
        print(f"找不到檔案: {log_file}，請確認路徑。")
        return pd.DataFrame()
    
    # 1. 時間轉換為秒
    df['Time_s'] = df['Time_ms'] / 1000.0
    if log_file == IOPS_LOG_3 or log_file == BW_LOG_3:
        df['Time_s'] = df['Time_ms'] / 1000.0 + 30.0
    
    # 2. 單位轉換
    if log_type == 'bw':
        # FIO 的 bw log 單位為 KiB/s，轉換為 MiB/s
        df['Value'] = df['Value'] / 1024.0
    
    # 3. 去除極端值邏輯 (大於 10000 就用上一筆替代)
    # 使用 mask 將大於 10000 的變 NaN，再用 ffill 向前填補，最後用 bfill 處理首筆異常
    #limit = 10000
    #df['Value'] = df['Value'].mask(df['Value'] > limit).ffill().bfill()
        
    return df

def plot_metric(log1, log2, log3, log_type, title, ylabel, output_img):
    """將三個 Process 的數據畫在同一張圖上"""
    df1 = process_fio_log(log1, log_type)
    df2 = process_fio_log(log2, log_type)
    df3 = process_fio_log(log3, log_type)

    # 開始繪圖
    plt.figure(figsize=(12, 6), dpi=120)

    # 定義繪圖設定，方便迴圈處理
    datasets = [
        (df1, 'A - victim', 'blue'),
        (df2, 'B - victim', 'red'),
        (df3, 'C - interference', 'green')
    ]

    for df, label, color in datasets:
        if not df.empty:
            plt.plot(df['Time_s'], df['Value'], 
                     label=label, color=color, linewidth=1.2, alpha=0.8)

    # 圖表細節設定
    plt.title(title, fontsize=16, fontweight='bold')
    plt.xlabel("Time (Seconds)", fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.ylim(0) # 確保 Y 軸從 0 開始
    plt.legend(loc='upper right', fontsize=11)
    
    # 儲存圖表
    plt.tight_layout()
    plt.savefig(output_img)
    print(f"圖表已成功輸出至 {output_img}\n")
    plt.close()

if __name__ == "__main__":
    # 確保輸出資料夾存在
    import os
    os.makedirs("../Pictures/Screenshots/260512/", exist_ok=True)

    # 繪製 IOPS 圖表
    plot_metric(IOPS_LOG_1, IOPS_LOG_2, IOPS_LOG_3, log_type='iops',
                title="noisy neighbor",
                ylabel="IOPS",
                output_img="../Pictures/Screenshots/260512/NN_iops_max=100mbs.png")

    # 繪製 Bandwidth 圖表
    plot_metric(BW_LOG_1, BW_LOG_2, BW_LOG_3, log_type='bw',
                title="noisy neighbor",
                ylabel="Bandwidth (MiB/s)",
                output_img="../Pictures/Screenshots/260512/NN_bws_max=100mbs.png")