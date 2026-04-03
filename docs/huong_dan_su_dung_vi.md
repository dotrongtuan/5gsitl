# Mô Tả Dự Án Và Hướng Dẫn Sử Dụng

## 1. Mục đích dự án

`5g-nr-sitl-omnetpp-testbed` là môi trường mô phỏng 5G NR SA hoàn toàn bằng phần mềm để phục vụ nghiên cứu, kiểm thử và trình diễn.

Hệ thống kết hợp các thành phần chính sau:

- `Open5GS` làm 5G Core
- `srsRAN Project` làm gNB
- `srsRAN 4G srsUE` làm UE phần mềm
- `ZeroMQ` làm đường truyền IQ ảo giữa gNB và UE
- `GNU Radio` làm lớp mô phỏng kênh
- `OMNeT++` làm giao diện trực quan hóa và giám sát runtime
- `Python` và `Bash` để điều phối, kiểm tra attach, chạy testcase và thu thập kết quả

Mục tiêu thực tế của repo là:

- dựng được phiên attach 5G SA bằng phần mềm
- cấp được IP UE từ core
- chạy testcase độ trễ / kết nối cơ bản
- có log, pcap và trạng thái runtime đủ rõ để debug

## 2. Kiến trúc tổng quan

Luồng chính của hệ thống:

1. `Open5GS` khởi tạo các NF như `NRF`, `AMF`, `SMF`, `UPF`, `AUSF`, `UDM`, `UDR`, `PCF`
2. `gNB` kết nối N2 tới `AMF`
3. `UE` tìm cell, đọc SIB1, thực hiện RA và RRC setup
4. `UE` gửi NAS registration đến core
5. Core xác thực, thiết lập policy và PDU session
6. `UE` nhận IP trong dải `10.45.0.0/16`
7. Adapter và OMNeT++ đọc trạng thái runtime để hiển thị

## 3. Baseline đang hoạt động

Đây là baseline attach đã xác nhận hoạt động trên nhánh hiện tại:

- Core:
  - `configs/core/amf_compat.yaml`
  - `configs/core/smf_compat.yaml`
  - `configs/core/pcf.yaml`
  - `configs/core/subscribers_compat.yaml`
- Cờ runtime:
  - `OPEN5GS_ENABLE_PCF=1`
  - `OPEN5GS_ENABLE_NSSF=0`
- RAN / RF:
  - `configs/gnb/gnb_zmq_compat.yaml`
  - `configs/ue/ue_zmq_compat.conf`
  - `configs/channel/bypass_compat.yaml`

Tín hiệu đúng của baseline:

- `bash scripts/check_attach.sh` trả về:
  - `{"attached": true, "ue_ip": "10.45.0.x"}`
- `outputs/runtime/channel_status.json` có:
  - `"mode": "direct-zmq"`

Tài liệu baseline chi tiết hơn nằm ở:

- `docs/runtime_compat_attach_baseline.md`

## 4. Yêu cầu môi trường

Khuyến nghị:

- Ubuntu `22.04` hoặc `24.04`
- MongoDB chạy được tại `mongodb://127.0.0.1/open5gs`
- Open5GS cài từ package Ubuntu / PPA
- GNU Radio có binding Python
- OMNeT++ `6.x`

Lưu ý:

- Trên Ubuntu `24.04`, bootstrap hiện dùng source build cho `srsRAN Project` và `srsRAN 4G`
- `PCF` phải có `db_uri` hợp lệ trong `configs/core/pcf.yaml`

## 5. Cài đặt nhanh

Nếu muốn dựng môi trường từ đầu:

```bash
bash scripts/bootstrap_ubuntu_sitl.sh
```

Script này sẽ:

- cài dependency hệ thống
- cài MongoDB và Open5GS
- cài hoặc build `srsRAN Project` và `srsRAN 4G`
- tạo Python virtualenv
- tạo `.env`
- provision subscriber
- build phần OMNeT++

## 6. Chạy demo một lệnh

Lệnh nhanh nhất để chạy full flow:

```bash
bash scripts/run_runtime_demo.sh
```

Script này sẽ:

1. setup network host
2. dừng stack cũ
3. khởi động Open5GS core
4. khởi động gNB
5. khởi động UE
6. khởi động channel emulator
7. khởi động adapter
8. mở OMNeT++ GUI nếu có
9. kiểm tra attach
10. chỉ chạy testcase nếu attach thành công

## 7. Kiểm tra attach

Sau khi stack đã chạy:

```bash
bash scripts/check_attach.sh
```

Kết quả mong đợi:

```json
{"attached": true, "ue_ip": "10.45.0.2"}
```

Kiểm tra thêm trạng thái channel:

```bash
cat outputs/runtime/channel_status.json
```

Kết quả mong đợi:

```json
{"mode": "direct-zmq", ...}
```

## 8. Chạy thủ công từng thành phần

Nếu muốn debug từng bước thay vì chạy demo:

```bash
bash scripts/setup_host_network.sh
bash scripts/start_core.sh
sleep 3
bash scripts/start_gnb.sh
sleep 2
bash scripts/start_ue.sh
sleep 2
bash scripts/start_channel.sh
bash scripts/start_adapters.sh
bash scripts/start_omnetpp_gui.sh
```

Sau đó:

```bash
bash scripts/check_attach.sh
```

## 9. Các file cấu hình quan trọng

### Core

- `configs/core/amf_compat.yaml`
  - AMF tối giản cho attach baseline
- `configs/core/smf_compat.yaml`
  - SMF tối giản cho DNN `internet`
- `configs/core/pcf.yaml`
  - PCF bắt buộc cho đường đăng ký hiện tại
- `configs/core/subscribers_compat.yaml`
  - subscriber mặc định `001010123456780`

### RAN

- `configs/gnb/gnb_zmq_compat.yaml`
  - gNB dùng band `n3`, `15 kHz SCS`, `20 MHz`
- `configs/ue/ue_zmq_compat.conf`
  - UE dùng `APN internet`, namespace `ue1`

### Channel

- `configs/channel/bypass_compat.yaml`
  - baseline attach đang dùng mode `direct-zmq`

## 10. Cách đọc log

Nhóm log nên xem đầu tiên khi attach lỗi:

```bash
tail -n 80 outputs/logs/open5gs/amf.stdout.log
tail -n 80 outputs/logs/open5gs/pcf.stdout.log
tail -n 80 outputs/logs/open5gs/udm.stdout.log
tail -n 80 outputs/logs/open5gs/udr.stdout.log
tail -n 120 outputs/logs/ue/ue.log
tail -n 120 outputs/logs/gnb/gnb.log
```

Nếu cần grep nhanh:

```bash
grep -nE "Registration request|Registration reject|UE Context Release|Cannot receive SBI message" outputs/logs/open5gs/amf.log
grep -nE "mongoc_collection_find_with_opts|Failure when receiving data from the peer" outputs/logs/open5gs/pcf.log
```

## 11. Sự cố thường gặp

### 11.1. `check_attach.sh` trả về `attached: false`

Kiểm tra lần lượt:

- `outputs/runtime/channel_status.json` có đang là `direct-zmq` không
- `AMF` có nhận `Registration request` không
- `UE` có vào đến bước NAS security không
- `PCF` có khởi tạo thành công và kết nối MongoDB không

### 11.2. AMF báo `No [npcf-am-policy-control]`

Nguyên nhân:

- `PCF` không chạy hoặc không được bật

Cần đảm bảo:

- `OPEN5GS_ENABLE_PCF=1`
- `open5gs-pcfd` có sẵn trong máy

### 11.3. PCF báo lỗi MongoDB collection null

Nguyên nhân:

- `configs/core/pcf.yaml` thiếu `db_uri`

Cần đảm bảo file này có:

```yaml
db_uri: mongodb://127.0.0.1/open5gs
```

### 11.4. Channel ở chế độ `dummy`

Nguyên nhân:

- Python đang chạy channel không import được GNU Radio

Khắc phục:

- ưu tiên dùng `/usr/bin/python3`
- kiểm tra `outputs/logs/channel/channel.stdout.log`

## 12. Test nhanh sau khi attach thành công

Sau khi attach được, có thể chạy testcase mặc định:

```bash
bash scripts/run_testcase.sh testcases/latency/baseline_rtt.yaml
```

Hoặc chạy lại demo đầy đủ:

```bash
bash scripts/run_runtime_demo.sh
```

## 13. Kết luận

Repo này hiện đã có một baseline SA attach hoạt động ổn định cho nhánh tương thích với `srsUE`.

Nếu mục tiêu là:

- xác nhận attach
- lấy UE IP
- chạy testcase cơ bản
- thu log để nghiên cứu

thì nên bám đúng bộ cấu hình tương thích đang được mô tả ở tài liệu này, thay vì chuyển sang profile rộng hơn ngay từ đầu.
