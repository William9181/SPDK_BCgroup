import pandas as pd
import matplotlib.pyplot as plt

# ================= 參數設定 =================
# 請替換為您實際的 FIO log 檔名
LOG1 = "benchmark_log/FIO/_lat.1.log" 
LOG2 = "benchmark_log/FIO/_lat.2.log"
LOG3 = "benchmark_log/FIO/_lat.3.log"
CHART_TITLE = "noisy neighbor"
Y_AXIS_UNIT = "us" # 支援 "ns", "us", "ms"

def process_fio_log(log_file):
    """讀取並解析單一 FIO log 檔案"""
    print(f"正在解析 {log_file} ...")
    df = pd.read_csv(log_file, header=None, usecols=range(4), 
                     names=['Time_ms', 'Latency_ns', 'DDIR', 'BlockSize'])
    
    # 時間轉換為秒
    df['Time_s'] = df['Time_ms'] / 1000.0
    
    # 延遲單位轉換
    if Y_AXIS_UNIT == "us":
        df['Latency'] = df['Latency_ns'] / 1000.0
    elif Y_AXIS_UNIT == "ms":
        df['Latency'] = df['Latency_ns'] / 1000000.0
    else:
        df['Latency'] = df['Latency_ns']
    
    #limit = 150000
    #df['Latency'] = df['Latency'].mask(df['Latency'] > limit.ffill()
    #df['Latency'] = df['Latency'].bfill()
        
    return df

def plot_combined_latency():
    # 讀取資料
    df_1 = process_fio_log(LOG1)
    df_2 = process_fio_log(LOG2)
    df_3 = process_fio_log(LOG3)

    
    df_3['Time_s'] = df_3['Time_s'] + 30.0
    
    # 開始繪圖
    plt.figure(figsize=(12, 6), dpi=120)

    # 繪製高優先權 (藍色)
    if not df_1.empty:
        plt.plot(df_1['Time_s'], df_1['Latency'], 
                 label='A - victim', color='blue', linewidth=1.5, alpha=0.8)

    # 繪製低優先權 (紅色)
    if not df_2.empty:
        plt.plot(df_2['Time_s'], df_2['Latency'], 
                 label='B - victim', color='red', linewidth=1.5, alpha=0.8)
        
    if not df_3.empty:
        plt.plot(df_3['Time_s'], df_3['Latency'], 
                 label='C - interference', color='green', linewidth=1.5, alpha=0.8)

    # 圖表設定
    plt.title(CHART_TITLE, fontsize=16, fontweight='bold')
    plt.xlabel("Time (Seconds)", fontsize=12)
    plt.ylabel(f"Latency ({Y_AXIS_UNIT})", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(loc='upper right', fontsize=11)
    
    # 若發現高優先權曲線被壓縮成一條線，可解除下方註解改用對數刻度 (Log Scale)
    # plt.yscale('log')

    # 儲存圖表
    output_img = "../Pictures/Screenshots/260512/NN_lat_max=100mbs.png"
    plt.tight_layout()
    plt.savefig(output_img)
    print(f"圖表已成功輸出至 {output_img}")

if __name__ == "__main__":
    plot_combined_latency()