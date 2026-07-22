# BCgroup : A Performance Isolation Framework in SPDK-Based Share Storages
本專案提供一套實作於 SPDK (Storage Performance Development Kit) bdev 層的效能隔離框架 (BCgroup)。  
透過自定義的虛擬區塊裝置 (Virtual Bdev) 與輪詢 (Poller) 機制，提供 `io.max`、`io.latency` 與 `io.weight` 等資源控制功能，藉此解決多租戶 NVMe-over-Fabrics (NVMe-oF) 共享儲存環境下的 Noisy Neighbor 效能干擾問題。 

## 目錄結構
* `bcgroup_framework.patch`: 包含 BCgroup 核心模組 (bdev/bcgroup) 與 SPDK 相關 Makefile 修改的修補檔。
* `benchmarks/`: 包含用於驗證效能隔離與 Noisy Neighbor 干擾測試的 FIO 設定檔與環境設定腳本。

## 1. 原始碼下載與 Patch 套用
確保你的系統已安裝編譯 SPDK 所需的相依套件（如 DPDK 依賴項）。本專案於 Ubuntu 環境下開發與測試。
為了確保相容性，請務必切換至本專案開發時所使用的 SPDK 版本。
```bash
# 下載 SPDK 官方原始碼
git clone https://github.com/spdk/spdk.git
cd spdk

# 切換至相容的 commit 版本
git checkout f288c545b6e9b9139b9e8671e8c7b3bf6fefa83d

# 下載並套用 BCgroup 修補檔
git clone https://github.com/William9181/SPDK_BCgroup.git
git apply SPDK_BCgroup/bcgroup_framework.patch
```

## 2. 編譯與建置
套用 Patch 後，BCgroup 模組已整合至 SPDK 的建置系統中。請執行標準的編譯流程：
```bash
# 初始化並下載所有需要的子模組
git submodule update --init
# 安裝系統相依套件 (若尚未安裝)
sudo ./scripts/pkgdep.sh

# 設定並編譯
./configure
# 如須使用 fio
./configure --with-fio=$(FIO_path)

# 編譯
make -j$(nproc)
```

## 3. 如何使用
首先要分配 Hugepages 並將 NVMe 跟 I/OAT 裝置從 kernel driver 當中解除綁定
```bash
# 環境設置腳本
sudo ./scripts/setup.sh
```

使用 Target Application 做為 Storage Server
```bash
# 啟用spdk_tgt 
sudo ./build/bin/spdk_tgt
``` 
  * -m : core mask (0xFFFF : 0 ~ 16 Core)  
  * --json : 按照json檔內容配置

掛載 SSD 至 spdk_nvme_controller  
```bash
sudo python3 scripts/rpc.py bdev_nvme_attach_controller -b Nvme0 -t PCIe -a $(PCI_ADDR)
``` 
  *  -b : block device name, -t : 協定
  *  -a : PCI_ADDR 為裝置位址，必須先解除綁定

掛載 BCgroup 模組
```bash
sudo python3 bcgroup_rpc.py bdev_bcgroup_create base_bdev_name=Nvme0 name=QosDisk0
``` 
  *  base_bdev_name : 對應之 block device
  *  name : bcgroup device name，io控制項皆使用此名稱

到這裡基本上就啟用 BCgroup 模組了，Client 端可直接讀寫裝置，或者透過 Nvme-oF 的方式將此裝置公開至網路上皆可使用！！

## 4. io控制項
檔案路徑 : /module/bdev/bcgroup  
  *  `io.max` : 用於限制單一群組在單位時間內可使用的最大 I/O 資源。    
  *  `io.latency` : 保護已設定延遲目標的群組，使其平均延遲不可高於目標延遲。  
  *  `io.weight` : 依照各群組設定的權重分配可用的I/O 派送能力。  

Remote Procedure Call 
  *  `io.stat` : 記錄各個 BCgroup 群組的 I/O 使用狀態。
```bash
sudo python3 bcgroup_rpc.py bdev_bcgroup_io_stat
```
  *  `io.pressure` : 用於觀察各個 BCgroup 群組在執行期間是否出現 I/O 壅塞情形。
```bash
sudo python3 bcgroup_rpc.py bdev_bcgroup_io_pressure
```

## 5. benchmarks 資料夾
此為作者於撰寫論文期間使用的環境設置, FIO benchmark及數據監控腳本等。  
