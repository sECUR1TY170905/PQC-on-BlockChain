# Kyber (ML-KEM-512) — Comparison Summary

## A. Traditional vs ML-KEM Confidential

| Metric | Traditional (ECDSA) | ML-KEM Confidential |
|---|---:|---:|
| **Auth/KEM time (s)**  | 0.016294  | 0.000115  |
| **Send+confirm (s)**   | 21.113796  | 10.155024  |
| **Gas used**           | 282619       | 334612       |
| **Crypto bytes**       | 65     | 768     |

## B. AES-256-GCM Encryption (Confidentiality)

| Metric | Value |
|---|---:|
| **Plaintext size (bytes)**   | 69 |
| **Encrypted size (bytes)**   | 101 |
| **Encryption time (s)**      | 0.007215 |
| **Decryption time (s)**      | 0.000234 |
| **Decrypt matches plaintext**| True |