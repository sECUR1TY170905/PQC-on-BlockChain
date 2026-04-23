# PQC on Blockchain Suite

This project is a comprehensive suite designed to evaluate, simulate, and compare **Post-Quantum Cryptography (PQC)** algorithms within a Blockchain environment (specifically EVM-compatible networks).

As quantum computing advances, traditional cryptographic algorithms like ECDSA (used in Bitcoin and Ethereum) become vulnerable. This project demonstrates how NIST-standardized PQC algorithms perform when integrated into smart contracts.

## 📊 Included PQC Algorithms

The suite is divided into two main categories:

### 1. Digital Signatures (Authentication & Integrity)
- **Dilithium (`ml_dsa_44`)**: Used as the baseline algorithm for signature-based demos.
- **Falcon (`falcon_512`)**: Run in parallel to compare performance and signature sizes against Dilithium.
- **SPHINCS+ (`sphincs_sha2_128f_simple`)**: A hash-based signature algorithm for further comparison.

### 2. Key Encapsulation Mechanism (Confidentiality)
- **Kyber (`ml_kem_512`)**: Used for confidentiality, establishing a shared secret, and secure key exchange.

---

## 🏗 Project Structure

- `shared/`: Contains the common Solidity Smart Contract (`Demo.sol`), ABI, and shared Python utilities (`common.py`). This ensures all algorithms are tested on an identical baseline.
- `algorithms/`: Contains the specific implementation and demo scripts for each PQC algorithm.
- `*.sh`: Quick-run shell scripts located in the root directory for executing each demo effortlessly.

---

## ⚙️ Prerequisites

Before running the suite, ensure you have the following installed:
- **Python 3.8+**
- **pip** (Python package manager)
- A local or remote Ethereum node (e.g., [Ganache](https://trufflesuite.com/ganache/), [Hardhat Network](https://hardhat.org/), or a Testnet like Sepolia via Infura/Alchemy).

---

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/<YOUR_USERNAME>/<REPO_NAME>.git
   cd pqc-algorithm-comparison-on-blockchain-main
   ```

2. **Install Python dependencies:**
   It is recommended to use a virtual environment.
   ```bash
   pip install -r shared/requirements.txt
   ```

3. **Environment Configuration:**
   Copy the example environment variables file and configure your parameters.
   ```bash
   cp .env.example .env
   ```
   Open the `.env` file and fill in:
   - `RPC_URL`: Your blockchain node URL (e.g., HTTP provider for Sepolia).
   - `PRIVATE_KEY`: Private key of your test wallet (⚠️ **NEVER use a mainnet wallet with real funds**).
   - `CONTRACT_ADDRESS`: The deployed address of `shared/contracts/Demo.sol`.

   *(Note: You need to deploy `Demo.sol` to your chosen network first and paste its address here).*

---

## 🏃 How to Run

You can easily test any of the algorithms using the provided shell scripts in the root directory.

Run **Dilithium** (Baseline Signature):
```bash
bash run_dilithium.sh
```

Run **Falcon**:
```bash
bash run_falcon.sh
```

Run **SPHINCS+**:
```bash
bash run_sphincs.sh
```

Run **Kyber** (KEM):
```bash
bash run_kyber.sh
```

### 📈 Expected Output
Upon execution, the scripts will connect to the configured blockchain, generate post-quantum keys, interact with the smart contract, and output metrics to the console. You should expect to see:
- Generated public/private key sizes.
- Encrypted/Signed payload sizes.
- **Gas consumption** for the on-chain transactions.
- Verification status on the blockchain.

---

## 📝 License
MIT License
