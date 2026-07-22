# In this readme

* [實現功能](#method)
* [怎麼跑Benchmark](#benchmark)

<a id="method"></a>
## 實現功能


<a id="benchmark"></a>
## 怎麼跑Benchmark
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
