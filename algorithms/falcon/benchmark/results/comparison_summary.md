# Falcon (falcon_512) — Comparison Summary

## A. Traditional vs PQC Hybrid

| Metric | Traditional (ECDSA) | PQC Hybrid (Falcon) |
|---|---:|---:|
| **Signing time (s)**  | 0.016361  | 0.006247  |
| **Send+confirm (s)**  | 14.371971  | 0.880870  |
| **Gas used**          | 248431       | 363933       |
| **Auth bytes**        | 65     | 658     |

## B. IPFS Off-chain Upload (Sender side)

| Metric | Value |
|---|---:|
| **Signature upload (s)**  | 0.013967 |
| **Public key upload (s)** | 0.018736 |
| **Total upload (s)**      | 0.032703 |

## C. End-to-End Verification (Receiver side)

| Metric | Value |
|---|---:|
| **Signature download (s)**  | 0.016133 |
| **Public key download (s)** | 0.009369 |
| **Hash comparison (s)**     | 0.000868 |
| **PQC verify (s)**          | 0.000247 |
| **E2E latency (s)**         | 0.026617 |
| **Verification passed**     | True |