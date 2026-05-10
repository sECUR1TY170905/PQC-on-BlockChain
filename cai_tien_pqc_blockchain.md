# Đề xuất cải tiến dự án: Hoàn thiện luồng xác minh PQC (End-to-End Verification)

## 1. Vấn đề của hệ thống hiện tại
- **Hạn chế:** Script hiện tại chỉ xác minh chữ ký PQC ngay tại thời điểm chạy (runtime) để đo tốc độ CPU, sau đó **loại bỏ** chữ ký này.
- **Hệ quả:** Dù Smart Contract có lưu `pqcProofHash` trên blockchain làm bằng chứng (timestamping), nhưng người nhận trong tương lai sẽ **không thể xác minh** được do không có chữ ký gốc (PQC Signature) để đối chiếu.

## 2. Giải pháp: Tích hợp hệ thống lưu trữ Off-chain (IPFS)
Để giải quyết bài toán kích thước chữ ký PQC quá lớn (lên tới hàng nghìn bytes) không thể lưu trực tiếp on-chain, hệ thống cần thêm một lớp lưu trữ phân tán.

**Quy trình gửi (Sender):**
1. Alice ký payload bằng PQC → `pqc_signature`.
2. Upload `pqc_signature` lên mạng IPFS → Nhận lại mã băm `ipfs_cid` (ví dụ: QmXyz...).
3. Tính `pqcProofHash = keccak256(payload + pqc_signature)`.
4. Gọi Smart Contract lưu: `payload`, `pqcProofHash`, và `ipfsCid`.

**Quy trình nhận và xác minh (Verifier/Bob):**
1. Tải bản ghi từ Blockchain để lấy `payload`, `pqcProofHash` và `ipfsCid`.
2. Dùng `ipfsCid` tải chữ ký PQC gốc từ IPFS về.
3. **Bước xác minh 1 (Toàn vẹn & Chống tráo đổi):** So sánh `keccak256(payload + chữ ký tải về)` có khớp với `pqcProofHash` trên chain hay không?
4. **Bước xác minh 2 (Xác thực người gửi):** Chạy hàm `ml_dsa_44.verify(public_key, payload, chữ ký tải về)` để đảm bảo đúng Alice ký.

## 3. Thay đổi về mặt mã nguồn (Code Changes)
- **Smart Contract (`Demo.sol`):** Thêm trường `string ipfsCid` vào struct `Record`.
- **Sender Script:** Tích hợp thư viện `ipfshttpclient` để gọi lệnh `client.add_bytes(pqc_signature)`.
- **Verifier Script (Tạo mới):** Viết thêm một script `verify_e2e.py` chuyên đóng vai trò người nhận đi bóc tách giao dịch và xác minh.

## 4. Bổ sung các chỉ số đo lường Benchmark mới
Giữ nguyên các chỉ số hiệu năng thuật toán hiện tại, định nghĩa thêm nhóm chỉ số **Hiệu năng Hệ thống (System Performance)**:

* `ipfs_upload_seconds`: Thời gian tải chữ ký lên IPFS.
* `ipfs_download_seconds`: Thời gian tải chữ ký từ IPFS về.
* `hash_comparison_seconds`: Thời gian băm và so sánh chuỗi (cực nhỏ).
* **`e2e_verification_latency` (Tổng độ trễ xác minh):** Bằng tổng thời gian Download + So sánh Hash + Thời gian chạy thuật toán PQC Verify (`pqc_verify_seconds`).

## 5. Giá trị mang lại cho báo cáo/đồ án
Cải tiến này chuyển đổi dự án từ một **"Bài đo lường hiệu năng CPU"** thành một **"Mô hình kiến trúc bảo mật Hybrid thực tế"**, chứng minh được cách giải quyết triệt để vấn đề "Làm sao dùng chữ ký khổng lồ của PQC trong môi trường eo hẹp của Blockchain".
