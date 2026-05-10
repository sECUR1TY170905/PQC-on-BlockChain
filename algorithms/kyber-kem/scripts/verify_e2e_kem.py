"""End-to-end decapsulation and decryption for Kyber records stored on-chain."""

from __future__ import annotations

import argparse
import time
import hashlib

from pqcrypto.kem import ml_kem_512
from Crypto.Cipher import AES

from common import (
    DEFAULT_ABI_PATH,
    build_web3,
    load_abi,
    load_dotenv,
    require_env,
    write_result,
)
from offchain_storage import load_kem_ciphertext, storage_backend_name


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify a Kyber record end-to-end.")
    parser.add_argument("--record-id", type=int, required=True, help="On-chain record id to decrypt")
    parser.add_argument(
        "--secret-key-path",
        default="kyber_secret.bin",
        help="Path to the local Kyber secret key file",
    )
    return parser.parse_args()


def fetch_record(contract, record_id: int) -> dict[str, object]:
    (
        fetched_record_id,
        owner,
        payload,
        payload_hash,
        pqc_proof_hash,
        app_nonce,
        timestamp,
        encrypted,
        mode,
        ipfs_cid,
        algorithm,
    ) = contract.functions.getRecord(record_id).call()

    return {
        "record_id": fetched_record_id,
        "owner": owner,
        "payload": payload,
        "payload_hash": payload_hash.hex() if isinstance(payload_hash, bytes) else payload_hash,
        "kem_proof_hash": pqc_proof_hash.hex() if isinstance(pqc_proof_hash, bytes) else pqc_proof_hash,
        "app_nonce": app_nonce,
        "timestamp": timestamp,
        "encrypted": encrypted,
        "mode": mode,
        "ipfs_cid": ipfs_cid,
        "algorithm": algorithm,
    }


def add_hex_prefix(value: str) -> str:
    return value if value.startswith("0x") else f"0x{value}"


def derive_aes_key(shared_secret: bytes) -> bytes:
    return hashlib.sha256(shared_secret).digest()


def decrypt_payload(key: bytes, payload: bytes) -> tuple[bytes, float]:
    start = time.perf_counter()
    nonce = payload[:16]
    tag = payload[16:32]
    ciphertext = payload[32:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    elapsed = time.perf_counter() - start
    return plaintext, round(elapsed, 6)


def main() -> None:
    args = parse_args()
    load_dotenv()

    rpc_url = require_env("RPC_URL")
    contract_address = require_env("CONTRACT_ADDRESS")
    abi_path = require_env("CONTRACT_ABI_PATH", str(DEFAULT_ABI_PATH))

    with open(args.secret_key_path, "rb") as f:
        secret_key = f.read()

    w3 = build_web3(rpc_url)
    abi = load_abi(abi_path)
    contract = w3.eth.contract(address=w3.to_checksum_address(contract_address), abi=abi)

    record = fetch_record(contract, args.record_id)
    if record["record_id"] == 0:
        raise RuntimeError(f"Record {args.record_id} does not exist")

    kem_ciphertext, ciphertext_path, ciphertext_download_seconds = load_kem_ciphertext(str(record["ipfs_cid"]))

    hash_start = time.perf_counter()
    recomputed_payload_hash = w3.to_hex(w3.keccak(record["payload"]))
    recomputed_proof_hash = w3.to_hex(w3.keccak(record["payload"] + kem_ciphertext))
    payload_hash_matches = recomputed_payload_hash == add_hex_prefix(str(record["payload_hash"]))
    proof_hash_matches = recomputed_proof_hash == add_hex_prefix(str(record["kem_proof_hash"]))
    hash_comparison_seconds = round(time.perf_counter() - hash_start, 6)

    decaps_start = time.perf_counter()
    shared_secret_dec = ml_kem_512.decrypt(secret_key, kem_ciphertext)
    kem_decaps_seconds = round(time.perf_counter() - decaps_start, 6)

    aes_key = derive_aes_key(shared_secret_dec)
    try:
        plaintext, decrypt_seconds = decrypt_payload(aes_key, record["payload"])
        decrypt_matches = True
    except Exception:
        plaintext = b""
        decrypt_seconds = 0.0
        decrypt_matches = False

    e2e_verification_latency = round(
        ciphertext_download_seconds
        + hash_comparison_seconds
        + kem_decaps_seconds
        + decrypt_seconds,
        6,
    )

    result = {
        "record_id": record["record_id"],
        "owner": record["owner"],
        "mode": record["mode"],
        "algorithm": record["algorithm"],
        "ipfs_cid": record["ipfs_cid"],
        "payload_hash_matches": payload_hash_matches,
        "proof_hash_matches": proof_hash_matches,
        "decrypt_matches_plaintext": decrypt_matches,
        "verification_passed": payload_hash_matches and proof_hash_matches and decrypt_matches,
        "offchain_storage": {
            "storage_backend": storage_backend_name(),
            "ciphertext_path": str(ciphertext_path),
        },
        "benchmark": {
            "ciphertext_download_seconds": ciphertext_download_seconds,
            "hash_comparison_seconds": hash_comparison_seconds,
            "kem_decaps_seconds": kem_decaps_seconds,
            "aes_decrypt_seconds": decrypt_seconds,
            "e2e_verification_latency": e2e_verification_latency,
        },
    }
    output_path = write_result("verify_e2e_result.json", result)

    print("Kyber End-to-End Decryption")
    print(f"Record ID: {record['record_id']}")
    print(f"Payload Hash Match: {payload_hash_matches}")
    print(f"Proof Hash Match: {proof_hash_matches}")
    print(f"AES Decryption Success: {decrypt_matches}")
    print(f"Verification Passed: {result['verification_passed']}")
    print(f"Result File: {output_path}")


if __name__ == "__main__":
    main()
