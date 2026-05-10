# Phân Tích Toàn Diện Dự Án: PQC Algorithm Comparison on Blockchain

---

## 1. TỔNG QUAN HỆ THỐNG

Dự án là một **bộ thử nghiệm (benchmark suite)** nhằm đánh giá và so sánh hiệu năng của các thuật toán **Mật mã Hậu lượng tử (Post-Quantum Cryptography - PQC)** được chuẩn hóa bởi NIST khi tích hợp vào môi trường Blockchain tương thích EVM (Ethereum Virtual Machine). Dự án mô phỏng các kịch bản thực tế trên mạng Ethereum (Sepolia Testnet) để đo lường gas tiêu thụ, độ trễ giao dịch, kích thước khóa/chữ ký, và khả năng chịu lỗi.

> **Vấn đề cốt lõi được giải quyết:** Các blockchain hiện tại như Ethereum sử dụng ECDSA (Elliptic Curve Digital Signature Algorithm), vốn **dễ bị phá vỡ bởi máy tính lượng tử** thông qua thuật toán Shor. Dự án này minh chứng rằng các thuật toán PQC có thể được tích hợp vào blockchain như một lớp bảo mật bổ sung.

### Vai trò của từng thuật toán PQC

| Thuật toán | Danh mục NIST | Vai trò trong Blockchain | Cơ sở toán học |
|---|---|---|---|
| **CRYSTALS-Dilithium** (`ml_dsa_44`) | Chữ ký số (Baseline) | Ký và xác thực tính toàn vẹn của payload giao dịch trước khi gửi lên chain | Lattice (Module-LWE) |
| **Falcon** (`falcon_512`) | Chữ ký số | So sánh hiệu năng ký/xác thực với Dilithium; nổi bật với chữ ký nhỏ hơn | Lattice (NTRU) |
| **SPHINCS+** (`sphincs_sha2_128f_simple`) | Chữ ký số | So sánh cách tiếp cận dựa trên hàm băm; không dùng lattice | Hash-based |
| **Kyber** (`ml_kem_512`) | Trao đổi khóa (KEM) | Thiết lập shared secret để mã hóa AES-256-GCM, bảo vệ tính bí mật của payload | Lattice (Module-LWE) |

**Lưu ý kiến trúc quan trọng:** Dự án dùng mô hình **Hybrid** – PQC xử lý bảo mật ở tầng ứng dụng (off-chain), còn ECDSA vẫn là cơ chế ký giao dịch Ethereum tiêu chuẩn (on-chain). Điều này đảm bảo tương thích ngược hoàn toàn với Ethereum.

---

## 2. LUỒNG HOẠT ĐỘNG HỆ THỐNG (WORKFLOW)

Mỗi kịch bản demo chạy theo luồng 7 bước sau:

```
[1] Đọc cấu hình (.env)
      ↓
[2] Kết nối Blockchain (RPC)
      ↓
[3] Sinh cặp khóa PQC
      ↓
[4] Xử lý Payload (ký hoặc mã hóa)
      ↓
[5] Build & Ký giao dịch Ethereum (ECDSA)
      ↓
[6] Gửi giao dịch lên Blockchain & Chờ xác nhận
      ↓
[7] Lưu kết quả benchmark (JSON/PNG/MD)
```

### Chi tiết từng bước

#### Bước 1 – Đọc cấu hình
- **File:** `.env` (gốc) hoặc `.env` cục bộ của từng algorithm
- **Code:** `shared/python/common.py` → hàm `load_dotenv()`
- Nạp `RPC_URL`, `PRIVATE_KEY`, `CONTRACT_ADDRESS`, `TX_TIMEOUT_SECONDS`

#### Bước 2 – Kết nối Blockchain
- **Code:** `common.py` → hàm `build_web3(rpc_url)`
- Tạo kết nối HTTP tới Ethereum node (Ganache/Hardhat/Sepolia)
- Kiểm tra kết nối: `w3.is_connected()`

#### Bước 3 – Sinh cặp khóa PQC
- **File:** `algorithms/<algo>/scripts/pqc_demo.py`
- **Dilithium/Falcon/SPHINCS+:** `public_key, secret_key = ml_dsa_44.generate_keypair()`
- **Kyber:** `public_key, secret_key = ml_kem_512.generate_keypair()`
- Thời gian sinh khóa được đo bằng `time.perf_counter()`

#### Bước 4 – Xử lý Payload

**Kịch bản chữ ký (Dilithium/Falcon/SPHINCS+):**
```python
pqc_signature = ml_dsa_44.sign(secret_key, payload)
verified       = ml_dsa_44.verify(public_key, payload, pqc_signature)
pqc_proof_hash = w3.keccak(payload + pqc_signature)  # "Dấu ấn" PQC lưu on-chain
```

**Kịch bản Kyber KEM:**
```python
kem_ciphertext, shared_secret = ml_kem_512.encrypt(public_key)  # Encapsulation
shared_secret_dec = ml_kem_512.decrypt(secret_key, kem_ciphertext)  # Decapsulation
aes_key = sha256(shared_secret)
ciphertext = AES_GCM.encrypt(aes_key, plaintext)
```

#### Bước 5 – Build & Ký giao dịch Ethereum
- **File:** tất cả `scripts/*.py`
- Gọi `contract.functions.storeRecord(...).build_transaction({...})`
- Ký bằng ECDSA tiêu chuẩn: `acct.sign_transaction(tx)`
- Dữ liệu gửi lên: payload, payload_hash, pqc_proof_hash, app_nonce

#### Bước 6 – Gửi & Chờ xác nhận
- `w3.eth.send_raw_transaction(raw_tx)`
- `w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)`
- Lấy gas tiêu thụ từ `receipt.gasUsed`

#### Bước 7 – Lưu kết quả
- **File:** `benchmark/compare.py` → JSON + biểu đồ PNG
- **File:** `benchmark/compare_availability.py` → bảng Markdown tổng hợp
- Kết quả lưu tại: `algorithms/<algo>/benchmark/results/`

---

## 3. CẤU TRÚC THƯ MỤC CHI TIẾT

```
pqc-algorithm-comparison-on-blockchain/
├── .env                        ← Cấu hình bí mật thực tế (KHÔNG commit)
├── .env.example                ← Template cấu hình mẫu
├── .gitignore
├── README.md                   ← Hướng dẫn tổng quan
├── run_dilithium.sh            ← Script chạy toàn bộ demo Dilithium
├── run_falcon.sh               ← Script chạy toàn bộ demo Falcon
├── run_kyber.sh                ← Script chạy toàn bộ demo Kyber
├── run_sphincs.sh              ← Script chạy toàn bộ demo SPHINCS+
│
├── shared/                     ← Thành phần dùng chung
│   ├── requirements.txt        ← Danh sách thư viện Python
│   ├── contracts/
│   │   ├── Demo.sol            ← Smart Contract Solidity (trung tâm hệ thống)
│   │   └── DemoABI.json        ← ABI để Python giao tiếp với contract
│   └── python/
│       └── common.py           ← Thư viện tiện ích dùng chung
│
└── algorithms/
    ├── dilithium/              ← Module Dilithium (ML-DSA-44)
    ├── falcon/                 ← Module Falcon-512
    ├── kyber-kem/              ← Module Kyber (ML-KEM-512)
    └── sphincs-plus/           ← Module SPHINCS+
```

Mỗi `algorithms/<algo>/` có cấu trúc giống nhau:
```
<algo>/
├── .env.example                ← Override cấu hình cục bộ cho thuật toán này
├── README.md                   ← Mô tả riêng
├── scripts/                    ← Code demo/benchmark chính
│   ├── common.py               ← Wrapper cục bộ (tái export shared/common.py)
│   ├── traditional_demo.py     ← Demo baseline ECDSA thuần
│   ├── pqc_demo.py             ← Demo Hybrid PQC + ECDSA (chỉ algo chữ ký)
│   ├── integrity_cases.py      ← Kiểm thử tính toàn vẹn (chỉ algo chữ ký)
│   ├── confidentiality_demo.py ← Demo tính bí mật AES+PQC
│   └── availability_benchmark.py ← Benchmark khả năng sẵn sàng (nhiều lần)
└── benchmark/
    ├── compare.py              ← So sánh traditional vs PQC (tạo PNG)
    ├── compare_availability.py ← Tạo bảng tổng hợp Markdown
    └── results/               ← Kết quả JSON, PNG, MD được sinh tự động
```

---

## 4. PHÂN TÍCH CHI TIẾT TỪNG FILE QUAN TRỌNG

### 4.1 `shared/contracts/Demo.sol` – Trung tâm lưu trữ On-chain

Đây là **Smart Contract Solidity** được deploy lên Ethereum. Toàn bộ các script Python đều gọi vào đây.

```solidity
struct Record {
    uint256 recordId;
    address owner;
    bytes   payload;        // Nội dung thực tế (plaintext hoặc AES ciphertext)
    bytes32 payloadHash;    // Keccak256 của payload (kiểm tra tính toàn vẹn)
    bytes32 pqcProofHash;   // Keccak256(payload + pqc_signature) = "Bằng chứng PQC"
    uint256 appNonce;       // Chống replay attack
    uint256 timestamp;
    bool    encrypted;      // True nếu payload đã được mã hóa AES
    string  mode;           // "traditional" / "pqc_hybrid" / "pqc_confidential"
}
```

**Hàm quan trọng:**

| Hàm | Mục đích |
|---|---|
| `storeRecord(...)` | Lưu một bản ghi mới. Kiểm tra `appNonce > lastNonceBySender` (chống replay) và `keccak256(payload) == payloadHash` (kiểm tra toàn vẹn) |
| `getRecord(recordId)` | Truy xuất bản ghi theo ID |

**Cơ chế chống Replay Attack (Anti-Replay):**
```solidity
require(appNonce > lastNonceBySender[msg.sender], "stale nonce");
lastNonceBySender[msg.sender] = appNonce;
```
Nonce được tạo từ `time.time_ns()` (nanosecond timestamp) ở phía Python → luôn tăng → không thể dùng lại giao dịch cũ.

**Tại sao chữ ký PQC không lưu trực tiếp on-chain?**
Chữ ký Dilithium (`ml_dsa_44`) có kích thước **~2420 bytes**, Falcon **~666 bytes**. Lưu trực tiếp sẽ tốn cực nhiều gas. Thay vào đó, dự án lưu `pqcProofHash = keccak256(payload + signature)` chỉ 32 bytes — đây là một **thiết kế kỹ thuật rất thực tế**.

---

### 4.2 `shared/python/common.py` – Thư viện tiện ích

Module trung tâm được import bởi **tất cả** các script demo.

| Hàm | Chức năng |
|---|---|
| `load_dotenv()` | Nạp biến môi trường từ cả 2 tầng `.env` (suite-level rồi project-level override) |
| `require_env(name)` | Lấy biến môi trường bắt buộc; thoát chương trình nếu thiếu |
| `build_web3(rpc_url)` | Kết nối Ethereum node qua HTTP Provider |
| `load_abi(path)` | Đọc file `DemoABI.json` để Python biết cách gọi Smart Contract |
| `build_app_metadata()` | Sinh `app_nonce` (nanoseconds) và `timestamp` (seconds) |
| `write_result(filename, payload)` | Ghi kết quả JSON ra thư mục `benchmark/results/` |

---

### 4.3 `scripts/pqc_demo.py` – Demo Hybrid PQC (Dilithium/Falcon/SPHINCS+)

**Luồng chính:**
1. Sinh cặp khóa PQC → đo thời gian
2. Ký payload → đo thời gian
3. Xác minh chữ ký → đo thời gian
4. Tính `pqc_proof_hash = keccak256(payload + signature)`
5. Gọi `storeRecord()` trên smart contract
6. Xuất kết quả JSON với đầy đủ metrics

**Dữ liệu benchmark được thu thập:**
```python
"pqc": {
    "algorithm": "ml_dsa_44",
    "public_key_size_bytes": 1312,   # Dilithium: 1312 bytes
    "secret_key_size_bytes": 2528,   # vs ECDSA: 32 bytes!
    "signature_size_bytes": 2420,    # vs ECDSA: 65 bytes!
},
"benchmark": {
    "pqc_keygen_seconds": ...,
    "pqc_sign_seconds": ...,
    "pqc_verify_seconds": ...,
    "ecdsa_sign_seconds": ...,
    "gas_used": ...,
}
```

---

### 4.4 `scripts/confidentiality_demo.py` – Demo Tính Bí Mật

**Kịch bản (Dilithium/SPHINCS+/Falcon):** Dùng PQC để ký + AES-GCM để mã hóa
```python
aes_key = sha256(CONFIDENTIALITY_SECRET)  # Khóa AES 256-bit từ secret
cipher  = AES.new(aes_key, AES.MODE_GCM)
payload = nonce(16 bytes) + tag(16 bytes) + ciphertext
```
Payload được mã hóa rồi MỚI ký bằng PQC → lưu lên chain.

**Kịch bản (Kyber - `kem_confidentiality_demo.py`):** Dùng Kyber KEM để sinh khóa AES
```python
kem_ciphertext, shared_secret = ml_kem_512.encrypt(public_key)   # Encapsulation
shared_secret_dec = ml_kem_512.decrypt(secret_key, kem_ciphertext)  # Decapsulation
aes_key = sha256(shared_secret)  # Khóa AES từ shared secret lượng tử an toàn
```
Đây là **điểm khác biệt mấu chốt**: Kyber không ký — nó **trao đổi khóa** để bảo vệ bí mật.

---

### 4.5 `scripts/integrity_cases.py` – Kiểm thử Tính Toàn Vẹn

Script này chứng minh 3 kịch bản vi phạm toàn vẹn và cho thấy hệ thống **tự động phát hiện**:

| Kịch bản | Cách thực hiện | Kết quả kỳ vọng |
|---|---|---|
| **Giả mạo payload** | `mutate_bytes(payload)` — lật bit đầu tiên | `ml_dsa_44.verify()` trả về `False` → không gửi TX |
| **Giả mạo chữ ký** | `mutate_bytes(signature)` — lật bit đầu tiên | `ml_dsa_44.verify()` trả về `False` → không gửi TX |
| **Replay Attack** | Gửi lại cùng `app_nonce` | Smart contract `revert("stale nonce")` |

```python
def mutate_bytes(value: bytes) -> bytes:
    mutated = bytearray(value)
    mutated[0] ^= 0x01  # XOR bit → thay đổi 1 bit duy nhất
    return bytes(mutated)
```
→ Minh chứng tính **collision resistance** của thuật toán PQC.

---

### 4.6 `scripts/availability_benchmark.py` – Benchmark Khả Năng Sẵn Sàng

Chạy N giao dịch liên tiếp (mặc định 5 lần) với cơ chế retry, đo:
- **Success rate** (tỷ lệ thành công)
- **Latency**: avg, P50, P95, P99
- **Throughput** (tx/giây)
- **Error classification**: timeout, contract_revert, nonce_conflict, rpc_error

```python
--mode  traditional | pqc_hybrid | pqc_confidential
--count 5           # số lần chạy
--max-retries 2     # số lần thử lại nếu thất bại
```

---

### 4.7 `benchmark/compare.py` & `compare_availability.py` – Phân tích kết quả

- **`compare.py`**: Đọc `traditional_result.json` + `pqc_result.json` → vẽ **biểu đồ thanh** so sánh (signing time, gas, auth size) bằng `matplotlib` → lưu `comparison.png`
- **`compare_availability.py`**: Tổng hợp 3 file JSON availability → tạo **bảng Markdown** → lưu `availability_summary.md`

---

### 4.8 `run_*.sh` – Điểm khởi chạy

Ví dụ `run_dilithium.sh` chạy tuần tự:
```bash
python3 scripts/traditional_demo.py        # 1. Baseline ECDSA
python3 scripts/pqc_demo.py               # 2. Hybrid PQC
python3 scripts/integrity_cases.py        # 3. Kiểm thử toàn vẹn
python3 scripts/confidentiality_demo.py   # 4. Demo bí mật
python3 scripts/availability_benchmark.py --mode traditional --count 5
python3 scripts/availability_benchmark.py --mode pqc_hybrid --count 5
python3 scripts/availability_benchmark.py --mode pqc_confidential --count 5
python3 benchmark/compare.py              # Vẽ biểu đồ
python3 benchmark/compare_availability.py # Tạo báo cáo Markdown
```

---

### 4.9 `shared/requirements.txt` – Môi trường cần thiết

```
web3          # Giao tiếp với Ethereum node (gửi TX, đọc contract)
eth-account   # Quản lý ví Ethereum, ký giao dịch ECDSA
pqcrypto      # Thư viện PQC: cung cấp ml_dsa_44, ml_kem_512, falcon_512, sphincs+
matplotlib    # Vẽ biểu đồ so sánh
pycryptodome  # AES-256-GCM (mã hóa đối xứng)
```

**Yêu cầu thiết lập:**
1. Python 3.8+
2. `pip install -r shared/requirements.txt`
3. Deploy `Demo.sol` lên Ethereum node (Ganache/Sepolia)
4. Điền `RPC_URL`, `PRIVATE_KEY`, `CONTRACT_ADDRESS` vào `.env`

---

## 5. ĐÁNH GIÁ KỸ THUẬT CỐT LÕI

### 5.1 Xử lý kích thước khóa/chữ ký lớn của PQC

So sánh kích thước thực tế (bytes):

| Tham số | ECDSA (truyền thống) | Dilithium (PQC) | Falcon (PQC) | SPHINCS+ (PQC) |
|---|---|---|---|---|
| Khóa công khai | 33–65 | **1,312** | **897** | **32** |
| Khóa bí mật | 32 | **2,528** | **1,281** | **64** |
| Chữ ký | 65 | **~2,420** | **~666** | **~17,088** |

**Giải pháp kỹ thuật của dự án:**
- **KHÔNG lưu toàn bộ chữ ký on-chain** → Lưu `pqcProofHash = keccak256(payload + signature)` (32 bytes cố định)
- Chữ ký PQC chỉ được xác minh **off-chain** trước khi gửi giao dịch
- Payload AES-encrypted được lưu on-chain (tăng gas do `bytes` dài hơn)

### 5.2 Đoạn code thể hiện rõ nhất kiến thức Mật mã học

**[1] Kyber KEM – Trao đổi khóa hậu lượng tử:**
```python
# Bên gửi: Encapsulation
kem_ciphertext, shared_secret_enc = ml_kem_512.encrypt(public_key)

# Bên nhận: Decapsulation
shared_secret_dec = ml_kem_512.decrypt(secret_key, kem_ciphertext)

# Cả hai bên có cùng shared_secret mà không cần truyền qua mạng!
assert shared_secret_enc == shared_secret_dec

# Dùng shared_secret để sinh khóa AES (KDF đơn giản dùng SHA-256)
aes_key = hashlib.sha256(shared_secret_enc).digest()
```
→ Minh họa hoàn hảo nguyên lý **Key Encapsulation Mechanism**.

**[2] PQC Proof Hash – Cam kết mật mã:**
```python
pqc_proof_hash = w3.keccak(payload + pqc_signature)
```
→ Là một **cryptographic commitment**: ai biết `payload` và `pqc_signature` đều có thể tái tạo hash này và so sánh với giá trị lưu on-chain để xác minh tính xác thực.

**[3] Integrity Check – Tính mẫn cảm của PQC với giả mạo:**
```python
mutated[0] ^= 0x01  # Chỉ thay đổi 1 bit
assert ml_dsa_44.verify(public_key, mutated_payload, signature) == False
```
→ Chứng minh **avalanche effect**: thay 1 bit → toàn bộ xác minh thất bại.

**[4] Anti-Replay trong Smart Contract:**
```solidity
require(appNonce > lastNonceBySender[msg.sender], "stale nonce");
```
→ Kết hợp tầng ứng dụng (Python nonce từ nanoseconds) + tầng blockchain (Solidity enforce) → bảo vệ 2 lớp.

### 5.3 Kết quả thực nghiệm

Từ file `availability_summary.md`:

| Mode | Success Rate | Avg Latency | Throughput | Avg Gas |
|---|---|---|---|---|
| Traditional (ECDSA only) | 100% | 11.17s | 0.087 tx/s | 248,392 |
| PQC Hybrid (ECDSA + Dilithium) | 100% | 16.07s | 0.061 tx/s | 268,650 |
| PQC Confidential (ECDSA + Dilithium + AES) | 100% | 11.35s | 0.086 tx/s | 311,759 |

**Nhận xét:**
- PQC Hybrid chậm hơn ~44% do overhead sinh khóa + ký Dilithium off-chain
- Gas tăng ~8% ở Hybrid (payload lớn hơn) và ~25% ở Confidential (ciphertext lớn hơn)
- Tất cả 3 mode đạt 100% success rate → PQC **khả thi** trong môi trường blockchain thực

---

## 6. SƠ ĐỒ KIẾN TRÚC TỔNG THỂ

```
┌─────────────────────────────────────────────────────────────┐
│                        TẦNG ỨNG DỤNG (Off-chain)            │
│                                                             │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐    │
│  │  Dilithium   │   │    Falcon    │   │   SPHINCS+   │    │
│  │  pqc_demo.py │   │  pqc_demo.py │   │  pqc_demo.py │    │
│  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘    │
│         │                  │                  │             │
│         └──────────────────┼──────────────────┘             │
│                            │ PQC Sign/Verify                │
│  ┌──────────────┐          │                                │
│  │  Kyber KEM   │          │                                │
│  │ kem_conf.py  │──KEM Enc/Dec──────────────────────────┐  │
│  └──────────────┘          │                           AES  │
│                            ▼                            │   │
│              ┌─────────────────────────┐                │   │
│              │     shared/common.py    │◄───────────────┘   │
│              │  build_web3, load_abi,  │                    │
│              │  write_result, ...      │                    │
│              └────────────┬────────────┘                    │
└───────────────────────────┼─────────────────────────────────┘
                            │ web3.py (HTTP JSON-RPC)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      TẦNG BLOCKCHAIN (On-chain)             │
│                                                             │
│         ┌───────────────────────────────────┐              │
│         │         Demo.sol (Contract)        │              │
│         │  storeRecord(payload,              │              │
│         │              payloadHash,          │              │
│         │              pqcProofHash,         │              │
│         │              appNonce, ...)        │              │
│         └───────────────────────────────────┘              │
│                    Ethereum Network                         │
│              (Ganache / Hardhat / Sepolia)                  │
└─────────────────────────────────────────────────────────────┘
```
