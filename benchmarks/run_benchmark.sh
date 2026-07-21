#!/bin/bash

# 確保腳本結束時殺掉背景程序
trap "kill 0" EXIT

echo "=========================================="
echo "           開始雙租戶競爭測試        "
echo "      High Prio (NS1) vs Low Prio (NS2)   "
echo "=========================================="

# 確保輸出目錄乾淨
rm -f ns1.log ns2.log

# 直接執行指令，不使用變數，避免引號問題
# 注意：最後面的 '&' 符號代表放入背景執行

echo "[High Prio] 啟動中..."
./build/bin/spdk_nvme_perf -c 0x2 -q 128 -o 4096 -w randread -t 60 \
    -r "trtype:TCP adrfam:IPv4 traddr:140.120.15.169 trsvcid:4420 subnqn:nqn.2016-06.io.spdk:cnode1 ns:1" \
    > benchmark_log/spdk_nvme_perf/ns1.log 2>&1 &

echo "[Low Prio] 啟動中..."
./build/bin/spdk_nvme_perf -c 0x4 -q 128 -o 4096 -w randread -t 60 \
    -r "trtype:TCP adrfam:IPv4 traddr:140.120.15.169 trsvcid:4420 subnqn:nqn.2016-06.io.spdk:cnode1 ns:2" \
    > benchmark_log/spdk_nvme_perf/ns2.log 2>&1 &

# 等待背景工作完成
echo "測試進行中，請稍候..."
wait

echo "=========================================="
echo "            測試完成！結果如下：            "
echo "=========================================="

echo "--- High Prio (NS1) 結果 ---"
if [ -s benchmark_log/spdk_nvme_perf/ns1.log ]; then
    sed -n '/^=\{10,\}/,$p' benchmark_log/spdk_nvme_perf/ns1.log
else
    echo " ns1.log 是空的，測試可能失敗，請檢查 log。"
fi
echo "--- Low Prio (NS2) 結果 ---"
if [ -s benchmark_log/spdk_nvme_perf/ns1.log ]; then
    sed -n '/^=\{10,\}/,$p' benchmark_log/spdk_nvme_perf/ns2.log
else
    echo " ns2.log 是空的，測試可能失敗，請檢查 log。"
fi
