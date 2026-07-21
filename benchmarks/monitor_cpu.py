import subprocess
import json
import time
import sys

RPC_CMD = ["sudo", "./scripts/rpc.py", "thread_get_stats"]
TARGET_THREAD = "nvmf_tgt_poll_group_000"

def get_stats():
    try:
        result = subprocess.run(RPC_CMD, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        for thread in data['threads']:
            if thread['name'] == TARGET_THREAD:
                return thread['busy'], thread['idle']
    except Exception as e:
        print(f"Error fetching stats: {e}")
    return 0, 0

print(f"開始監控 Thread: {TARGET_THREAD}")
print("按 Ctrl+C 停止監控...")
print("-" * 30)
print("Time(s), Busy(%)")

prev_busy, prev_idle = get_stats()
seconds = 0

try:
    while True:
        time.sleep(1) # 每秒取樣一次
        seconds += 1
        curr_busy, curr_idle = get_stats()

        # 計算這一秒內的 Delta (差值)
        delta_busy = curr_busy - prev_busy
        delta_idle = curr_idle - prev_idle
        total_delta = delta_busy + delta_idle

        if total_delta > 0:
            busy_pct = (delta_busy / total_delta) * 100
            # 輸出 CSV 格式，方便你之後複製到 Excel 畫圖
            print(f"{seconds}, {busy_pct:.2f}")
        else:
            print(f"{seconds}, 0.00")

        prev_busy, prev_idle = curr_busy, curr_idle

except KeyboardInterrupt:
    print("\n監控結束。")
    sys.exit(0)
