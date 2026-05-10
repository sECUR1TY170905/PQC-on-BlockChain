# Dilithium (ML-DSA-44) — Comparison Summary

## A. Traditional vs PQC Hybrid

| Metric | Traditional (ECDSA) | PQC Hybrid (Dilithium) |
|---|---:|---:|
| **Signing time (s)**  | 0.023490  | 0.000570  |
| **Send+confirm (s)**  | 4.110745  | 5.181970  |
| **Gas used**          | 277866       | 363921       |
| **Auth bytes**        | 65     | 2420     |

## B. IPFS Off-chain Upload (Sender side)

| Metric | Value |
|---|---:|
| **Signature upload (s)**  | 0.022967 |
| **Public key upload (s)** | 0.023808 |
| **Total upload (s)**      | 0.046775 |

## C. End-to-End Verification (Receiver side)

| Metric | Value |
|---|---:|
| **Signature download (s)**  | 0.024947 |
| **Public key download (s)** | 0.021925 |
| **Hash comparison (s)**     | 0.000177 |
| **PQC verify (s)**          | 0.000252 |
| **E2E latency (s)**         | 0.047301 |
| **Verification passed**     | True |