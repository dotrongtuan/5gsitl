# Hướng Dẫn Chạy Kịch Bản Thí Nghiệm, Thu Thập Và Đánh Giá Kết Quả

## 1. Mục tiêu tài liệu

Tài liệu này hướng dẫn:

- chọn và chạy một số kịch bản thí nghiệm tiêu biểu trong repo
- thu thập log, pcap, report, CSV và figure sau mỗi lần chạy
- đánh giá kết quả theo đúng khả năng hiện tại của pipeline

Phạm vi của tài liệu bám theo code hiện có trong:

- `scripts/run_testcase.sh`
- `tools/run_testcase.py`
- `scripts/export_results.sh`
- `tools/metrics_parser.py`
- `tools/plot_latency.py`
- `tools/pcap_analyzer.py`

## 2. Điều kiện trước khi chạy thí nghiệm

Trước khi chạy testcase, nên xác nhận baseline attach đã hoạt động:

```bash
source .venv/bin/activate || true
bash scripts/run_runtime_demo.sh
bash scripts/check_attach.sh
cat outputs/runtime/channel_status.json
```

Điều kiện tối thiểu:

- `check_attach.sh` trả về `{"attached": true, "ue_ip": "10.45.0.x"}`
- `channel_status.json` báo `"mode": "direct-zmq"`

Nếu baseline attach chưa ổn, xem:

- `docs/runtime_compat_attach_baseline.md`
- `docs/troubleshooting.md`

## 3. Cách chạy một testcase

Lệnh chung:

```bash
bash scripts/run_testcase.sh <testcase.yaml>
```

Ví dụ:

```bash
bash scripts/run_testcase.sh testcases/latency/baseline_rtt.yaml
```

Khi chạy, hệ thống sẽ:

1. đọc file YAML testcase
2. áp dụng NR profile
3. áp dụng slice profile nếu testcase có khai báo
4. bật capture tự động nếu `capture_config.enabled: true`
5. chạy traffic theo `traffic_config`
6. ghi `metrics.json`
7. sinh report JSON, MD, HTML và CSV
8. tắt capture

## 4. Một số kịch bản thí nghiệm nên chạy

### 4.1. Kịch bản 1: baseline attach và kết nối cơ bản

Mục tiêu:

- kiểm tra attach SA
- xác nhận UE nhận IP
- xác nhận ping cơ bản

Testcase:

```bash
bash scripts/run_testcase.sh testcases/nr/nr_baseline_connectivity.yaml
```

KPI nên xem:

- attach có thành công không
- `avg_rtt_ms`
- `packet_loss_pct`

Ngưỡng mục tiêu trong testcase:

- `attach_success: true`
- `max_avg_rtt_ms: 25`

### 4.2. Kịch bản 2: baseline RTT

Mục tiêu:

- lấy mốc RTT chuẩn để so với các profile/kênh khác

Testcase:

```bash
bash scripts/run_testcase.sh testcases/latency/baseline_rtt.yaml
```

KPI nên xem:

- `avg_rtt_ms`
- `p95_rtt_ms`
- `p99_rtt_ms`
- `jitter_ms`

Ngưỡng mục tiêu:

- `max_avg_rtt_ms: 25`
- `max_p95_rtt_ms: 35`

### 4.3. Kịch bản 3: low-latency / URLLC

Mục tiêu:

- kiểm tra profile low-latency và slice URLLC

Có thể chạy theo 2 cách:

Chạy trực tiếp testcase:

```bash
bash scripts/run_testcase.sh testcases/latency/low_latency_target.yaml
```

Hoặc chạy theo flow slice use case:

```bash
bash scripts/run_slice_usecase.sh configs/slicing/urllc.yaml testcases/slicing/urllc_ping.yaml
```

KPI nên xem:

- `avg_rtt_ms`
- `p95_rtt_ms`
- `packet_loss_pct`

Ngưỡng mục tiêu điển hình:

- `max_avg_rtt_ms: 15`
- `max_p95_rtt_ms: 25`

### 4.4. Kịch bản 4: tác động của kênh truyền

#### 4.4.1. AWGN nhẹ

```bash
bash scripts/run_testcase.sh testcases/phy/awgn_low.yaml
```

Mục tiêu:

- quan sát ảnh hưởng nhiễu nhẹ lên RTT và loss

#### 4.4.2. Trễ kênh 1 ms

```bash
bash scripts/run_testcase.sh testcases/phy/delay_1ms.yaml
```

Mục tiêu:

- so sánh `avg_rtt_ms` và `p95_rtt_ms` với `baseline_rtt`

Gợi ý đánh giá:

- chạy `baseline_rtt` trước
- chạy `delay_1ms` sau
- so sánh 2 file report JSON tương ứng

### 4.5. Kịch bản 5: eMBB / UDP streaming

Ví dụ:

```bash
bash scripts/run_testcase.sh testcases/nr/nr_embb_baseline.yaml
```

Hoặc:

```bash
bash scripts/run_slice_usecase.sh configs/slicing/embb.yaml testcases/slicing/embb_stream.yaml
```

Lưu ý quan trọng:

- các testcase này dùng `traffic_config.mode: udp-latency`
- script có chạy `iperf3`
- `tools/run_testcase.py` hiện đã parse các chỉ số UDP chính từ output `iperf3`
- các KPI có thể chấm tự động ở nhánh này là `min_throughput_mbps`, `max_loss_pct` và `max_jitter_ms`
- các KPI RTT như `max_avg_rtt_ms`, `max_p95_rtt_ms`, `max_p99_rtt_ms` vẫn không có dữ liệu thực trong nhánh `udp-latency`

Do đó:

- dùng các testcase này để tạo log và pcap là hợp lý
- có thể đánh giá tự động throughput, loss và jitter ngay trong report
- nếu testcase `udp-latency` vẫn khai báo KPI RTT, trạng thái đánh giá sẽ là `INCOMPLETE`

### 4.6. Chạy hàng loạt một nhóm testcase

Ví dụ chạy toàn bộ testcase latency:

```bash
python3 tools/run_suite.py testcases/latency
```

Ví dụ chạy toàn bộ testcase phy:

```bash
python3 tools/run_suite.py testcases/phy
```

Khuyến nghị:

- dùng suite cho regression
- dùng testcase đơn cho debug

## 5. Cách thu thập kết quả thí nghiệm

## 5.1. Kết quả sinh tự động sau `run_testcase`

Mỗi lần chạy testcase có thể tạo:

- `outputs/runtime/metrics.json`
- `outputs/reports/<testcase>.json`
- `outputs/reports/<testcase>.md`
- `outputs/reports/<testcase>.html`
- `outputs/csv/<testcase>.csv`
- `outputs/pcap/*.pcapng` nếu bật capture

## 5.2. Sinh thêm CSV, figure và pcap summary

Sau khi chạy testcase:

```bash
bash scripts/export_results.sh
```

Script này sẽ:

- chuyển `outputs/runtime/metrics.json` thành `outputs/csv/latency_latest.csv`
- vẽ `outputs/figures/latency_latest.png`
- phân tích pcap trong `outputs/pcap/`
- sinh summary tại `outputs/reports/pcap_summary.pcap.json`
- sinh flow CSV tại `outputs/csv/pcap_summary.pcap.csv`

## 5.3. Thu log gói gọn

Nếu muốn gom log để lưu hoặc chia sẻ:

```bash
bash scripts/collect_logs.sh
```

Kết quả:

- `outputs/reports/logbundle_<timestamp>.tar.gz`

## 5.4. Capture thủ công

Một số lựa chọn:

Capture toàn cục:

```bash
bash scripts/start_capture.sh manual
```

Capture N2:

```bash
bash scripts/capture_n2.sh manual
```

Capture N3:

```bash
bash scripts/capture_n3.sh manual
```

Capture host bridge:

```bash
bash scripts/capture_host_bridge.sh manual
```

Dừng capture:

```bash
bash scripts/stop_capture.sh
```

## 6. Cách đọc và đánh giá kết quả

## 6.1. Đánh giá KPI RTT

Nguồn chính:

- `outputs/reports/<testcase>.json`
- `outputs/csv/<testcase>.csv`
- `outputs/csv/latency_latest.csv`

Các chỉ số hiện có:

- `current_rtt_ms`
- `avg_rtt_ms`
- `p95_rtt_ms`
- `p99_rtt_ms`
- `packet_loss_pct`
- `jitter_ms`

Có thể xem nhanh:

```bash
cat outputs/reports/baseline_rtt.json
```

Hoặc:

```bash
python3 -m json.tool outputs/reports/baseline_rtt.json
```

Nguyên tắc đánh giá:

- `avg_rtt_ms` dùng để so sánh mức nền giữa các profile
- `p95_rtt_ms` và `p99_rtt_ms` phản ánh độ ổn định tail latency
- `packet_loss_pct` tăng khi kênh xấu hoặc attach/routing chưa ổn
- `jitter_ms` hữu ích khi đánh giá biến động trễ

## 6.2. So sánh với ngưỡng trong testcase

Mỗi testcase có mục:

- `expected_kpis`

Ví dụ:

```yaml
expected_kpis: { max_avg_rtt_ms: 25, max_p95_rtt_ms: 35 }
```

Lưu ý quan trọng:

- pipeline hiện đã tự động đánh giá `expected_kpis`
- kết quả được ghi vào `outputs/reports/<testcase>.json` trong trường `evaluation`
- ba trạng thái chính là:
  - `PASS`: tất cả KPI được chấm và đều đạt ngưỡng
  - `FAIL`: có ít nhất một KPI được chấm nhưng không đạt ngưỡng
  - `INCOMPLETE`: testcase có KPI không thể chấm tự động với traffic mode hiện tại hoặc KPI chưa được hỗ trợ

Nói ngắn gọn:

- testcase lưu KPI thực
- pipeline tự so sánh KPI thực với ngưỡng trong YAML
- người vận hành chỉ cần đọc phần `evaluation`

Có thể xem nhanh trạng thái đánh giá:

```bash
python3 -m tools.evaluate_testcase outputs/reports/<testcase>.json
```

Hoặc chỉ in trạng thái:

```bash
python3 -m tools.evaluate_testcase outputs/reports/<testcase>.json --summary-only
```

## 6.3. Đánh giá attach và kết nối

Đối với testcase connectivty / attach:

```bash
bash scripts/check_attach.sh
```

Kết quả mong đợi:

```json
{"attached": true, "ue_ip": "10.45.0.2"}
```

Đây là tiêu chí mạnh hơn việc chỉ nhìn log.

## 6.4. Đánh giá từ pcap

Phân tích tự động:

```bash
python3 -m tools.pcap_analyzer outputs/pcap --summary-only
```

Hoặc để sinh report đầy đủ:

```bash
python3 -m tools.pcap_analyzer outputs/pcap
```

Kết quả chính:

- `packet_count`
- `flow_count`
- top flow
- `rtt_approx_ms`
- `packet_loss_estimate_pct`

Điểm cần nhớ:

- phần ước lượng RTT trong `pcap_analyzer.py` hiện đáng tin nhất với ICMP echo
- với UDP stream, pcap hiện hữu ích chủ yếu để kiểm tra flow và số lượng packet, chưa phải bộ đo throughput hoàn chỉnh

## 6.5. Đánh giá testcase UDP / throughput

Với testcase như:

- `nr_embb_baseline`
- `embb_stream`
- `awgn_sweep`
- `fading_stress`

Hiện tại nên đánh giá theo cách sau:

1. đọc `outputs/logs/udp-latency-test.log`
2. kiểm tra output `iperf3`
3. dùng pcap để xác nhận có lưu lượng UDP đúng hướng
4. nếu report là `INCOMPLETE`, kiểm tra xem testcase có đang yêu cầu KPI RTT trên nhánh `udp-latency` hay không

Lý do:

- `tools/run_testcase.py` đã parse `throughput_mbps`, `packet_loss_pct` và `jitter_ms` từ `iperf3`
- nhánh `udp-latency` vẫn không tạo RTT thực ở mức ứng dụng như nhánh `ping`
- vì vậy report của testcase `udp-latency` chỉ có thể tự chấm đầy đủ khi `expected_kpis` dùng đúng các KPI mà mode này hỗ trợ

## 7. Quy trình khuyến nghị cho một thí nghiệm hoàn chỉnh

Ví dụ với thí nghiệm độ trễ:

1. chạy baseline attach:

```bash
bash scripts/check_attach.sh
```

2. chạy testcase:

```bash
bash scripts/run_testcase.sh testcases/latency/baseline_rtt.yaml
```

3. export kết quả:

```bash
bash scripts/export_results.sh
```

4. xem report:

```bash
cat outputs/reports/baseline_rtt.json
```

5. xem hình:

```bash
ls outputs/figures
```

6. nếu cần lưu toàn bộ log:

```bash
bash scripts/collect_logs.sh
```

## 8. Quy trình so sánh hai kịch bản

Ví dụ so sánh `baseline_rtt` và `delay_1ms`:

```bash
bash scripts/run_testcase.sh testcases/latency/baseline_rtt.yaml
bash scripts/run_testcase.sh testcases/phy/delay_1ms.yaml
```

Sau đó so sánh:

- `outputs/reports/baseline_rtt.json`
- `outputs/reports/delay_1ms.json`

Các chỉ số nên nhìn:

- `avg_rtt_ms`
- `p95_rtt_ms`
- `packet_loss_pct`
- `jitter_ms`

## 9. Kết luận thực dụng

Trong trạng thái hiện tại của repo:

- luồng `ping` là luồng có KPI thực đáng tin nhất
- `pcap_analyzer` hữu ích cho ICMP flow và loss
- `export_results.sh` đủ tốt để tạo report nhanh sau thí nghiệm
- testcase `udp-latency` hiện đã tự chấm được throughput, loss và jitter
- testcase `udp-latency` vẫn nên tránh khai báo KPI RTT nếu muốn có trạng thái `PASS/FAIL` đầy đủ

Nếu mục tiêu là đánh giá nhanh và chắc:

- ưu tiên chạy testcase `ping`
- dùng `baseline_rtt`, `low_latency_target`, `awgn_low`, `delay_1ms`, `nr_baseline_connectivity`

Nếu mục tiêu là mở rộng nghiên cứu:

- có thể chuẩn hóa thêm bộ KPI cho `udp-latency` để tránh `INCOMPLETE`
- có thể bổ sung thêm parser RTT ứng dụng cho nhánh UDP nếu cần đánh giá tail latency ở lớp traffic
