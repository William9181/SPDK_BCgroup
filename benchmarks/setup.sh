#!/bin/bash
set -e 

PCI_ADDR="0000:0d:00.0"
SUBNQN="nqn.2016-06.io.spdk:cnode1"

echo "Setting......"

echo "[1/5] 掛載實體 SSD (PCIe: $PCI_ADDR)..."
sudo python3 scripts/rpc.py bdev_nvme_attach_controller -b Nvme0 -t PCIe -a $PCI_ADDR
sleep 1 

echo "[2/5] 切割底層實體硬碟..."
sudo python3 scripts/rpc.py bdev_split_create Nvme0n1 3
sleep 1

echo "[3/5] 為每個切割區掛載獨立的 QoS 模組..."
# 這裡假設您的 RPC 指令支援在建立時就帶入 max_iops 參數 (例如 -m 2000)
# 如果您的 RPC 還沒支援，那它們初始會套用 C 語言裡的預設值
sudo python3 bcgroup_rpc.py bdev_bcgroup_create base_bdev_name=Nvme0n1p0 name=QosDisk0
sudo python3 bcgroup_rpc.py bdev_bcgroup_create base_bdev_name=Nvme0n1p1 name=QosDisk1
sudo python3 bcgroup_rpc.py bdev_bcgroup_create base_bdev_name=Nvme0n1p2 name=QosDisk2

echo "[4/5] 建立 NVMe-oF TCP 傳輸層與 Subsystem..."
sudo python3 scripts/rpc.py nvmf_create_transport -t TCP -u 16384 -m 8 -c 8192
sudo python3 scripts/rpc.py nvmf_create_subsystem $SUBNQN -a -s SPDK00000000000001 -d SPDK_Controller1

echo "[5/5] 將獨立的 QoS Namespace 掛載並監聽..."
sudo python3 scripts/rpc.py nvmf_subsystem_add_ns $SUBNQN QosDisk0
sudo python3 scripts/rpc.py nvmf_subsystem_add_ns $SUBNQN QosDisk1
sudo python3 scripts/rpc.py nvmf_subsystem_add_ns $SUBNQN QosDisk2
#sudo python3 scripts/rpc.py nvmf_subsystem_add_ns $SUBNQN Nvme0n1p0
#sudo python3 scripts/rpc.py nvmf_subsystem_add_ns $SUBNQN Nvme0n1p1
#sudo python3 scripts/rpc.py nvmf_subsystem_add_ns $SUBNQN Nvme0n1p2

sudo python3 scripts/rpc.py nvmf_subsystem_add_listener $SUBNQN -t tcp -a 140.120.15.169 -s 4420

echo "Success!"

