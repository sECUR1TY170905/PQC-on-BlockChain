"""Compare traditional baseline against ML-KEM confidentiality results."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt


RESULTS_DIR = Path(__file__).resolve().parent / "results"
TRADITIONAL_RESULT = RESULTS_DIR / "traditional_result.json"
KEM_RESULT = RESULTS_DIR / "kyber_confidentiality_result.json"
E2E_RESULT = RESULTS_DIR / "verify_e2e_result.json"
OUTPUT_PLOT = RESULTS_DIR / "comparison_kem.png"
OUTPUT_MD = RESULTS_DIR / "comparison_kem_summary.md"


def load_result(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing result file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def print_summary(traditional: dict, kem: dict, e2e: dict | None) -> None:
    print("=== Kyber (ML-KEM-512) Comparison Summary ===")
    print(f"  Traditional gas used   : {traditional['gas_used']}")
    print(f"  ML-KEM gas used        : {kem['gas_used']}")
    print(f"  Traditional sign time  : {traditional['benchmark']['ecdsa_sign_seconds']} s")
    print(f"  ML-KEM encaps time     : {kem['benchmark']['kem_encaps_seconds']} s")
    print(f"  ML-KEM decaps time     : {kem['benchmark']['kem_decaps_seconds']} s")
    print(f"  ML-KEM ciphertext size : {kem['kem']['ciphertext_size_bytes']} bytes")
    if "ciphertext_upload_seconds" in kem["benchmark"]:
        print(f"  IPFS ciphertext upload : {kem['benchmark']['ciphertext_upload_seconds']} s")
        print(f"  IPFS pubkey upload     : {kem['benchmark']['public_key_upload_seconds']} s")
    print(f"  AES encrypt time       : {kem['confidentiality']['encryption_seconds']} s")
    print(f"  AES decrypt time       : {kem['confidentiality']['decrypt_seconds']} s")
    if e2e:
        print(f"  E2E latency            : {e2e['benchmark']['e2e_verification_latency']} s")
        print(f"  Verification passed    : {e2e['verification_passed']}")


def save_plot_and_md(traditional: dict, kem: dict, e2e: dict | None) -> tuple[Path, Path]:
    has_ipfs = "ciphertext_upload_seconds" in kem["benchmark"]
    has_e2e = e2e is not None

    trad_sign    = traditional["benchmark"]["ecdsa_sign_seconds"]
    kem_time     = kem["benchmark"]["kem_encaps_seconds"] + kem["benchmark"]["kem_decaps_seconds"]
    trad_confirm = traditional["benchmark"]["send_and_confirm_seconds"]
    kem_confirm  = kem["benchmark"]["send_and_confirm_seconds"]
    trad_gas     = traditional["gas_used"]
    kem_gas      = kem["gas_used"]
    trad_bytes   = traditional["benchmark"]["signature_size_bytes"]
    kem_bytes    = kem["kem"]["ciphertext_size_bytes"]
    aes_enc      = kem["confidentiality"]["encryption_seconds"]
    aes_dec      = kem["confidentiality"]["decrypt_seconds"]
    plain_size   = kem["confidentiality"]["plaintext_size_bytes"]
    enc_size     = kem["confidentiality"]["encrypted_payload_size_bytes"]

    ipfs_ct_up = kem["benchmark"].get("ciphertext_upload_seconds", 0)
    ipfs_pk_up = kem["benchmark"].get("public_key_upload_seconds", 0)

    e2e_latency = e2e["benchmark"]["e2e_verification_latency"] if has_e2e else None
    ct_dl       = e2e["benchmark"]["ciphertext_download_seconds"] if has_e2e else None
    hash_cmp    = e2e["benchmark"]["hash_comparison_seconds"] if has_e2e else None
    kem_decaps  = e2e["benchmark"]["kem_decaps_seconds"] if has_e2e else None
    aes_dec_e2e = e2e["benchmark"]["aes_decrypt_seconds"] if has_e2e else None

    # --- Markdown ---
    md = [
        "# Kyber (ML-KEM-512) — Comparison Summary",
        "",
        "## A. Traditional vs ML-KEM Confidential",
        "",
        "| Metric | Traditional (ECDSA) | ML-KEM Confidential |",
        "|---|---:|---:|",
        f"| **Auth/KEM time (s)**  | {trad_sign:.6f}  | {kem_time:.6f}  |",
        f"| **Send+confirm (s)**   | {trad_confirm:.6f}  | {kem_confirm:.6f}  |",
        f"| **Gas used**           | {trad_gas}       | {kem_gas}       |",
        f"| **Crypto bytes**       | {trad_bytes}     | {kem_bytes}     |",
    ]
    if has_ipfs:
        md += [
            "",
            "## B. IPFS Off-chain Upload (Sender side)",
            "",
            "| Metric | Value |",
            "|---|---:|",
            f"| **Ciphertext upload (s)** | {ipfs_ct_up:.6f} |",
            f"| **Public key upload (s)** | {ipfs_pk_up:.6f} |",
        ]

    md += [
        "",
        "## C. AES-256-GCM Encryption (Confidentiality)",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| **Plaintext size (bytes)**   | {plain_size} |",
        f"| **Encrypted size (bytes)**   | {enc_size} |",
        f"| **Encryption time (s)**      | {aes_enc:.6f} |",
        f"| **Decryption time (s)**      | {aes_dec:.6f} |",
        f"| **Decrypt matches plaintext**| {kem['confidentiality']['decrypt_matches_plaintext']} |",
    ]
    if has_e2e:
        md += [
            "",
            "## D. End-to-End Decryption (Receiver side)",
            "",
            "| Metric | Value |",
            "|---|---:|",
            f"| **Ciphertext download (s)** | {ct_dl:.6f} |",
            f"| **Hash comparison (s)**     | {hash_cmp:.6f} |",
            f"| **KEM decapsulation (s)**   | {kem_decaps:.6f} |",
            f"| **AES decryption (s)**      | {aes_dec_e2e:.6f} |",
            f"| **E2E latency (s)**         | {e2e_latency:.6f} |",
            f"| **Verification passed**     | {e2e['verification_passed']} |",
        ]
    OUTPUT_MD.write_text("\n".join(md), encoding="utf-8")

    # --- 8 subplots (2x4) ---
    fig, axs = plt.subplots(2, 4, figsize=(20, 8))
    fig.suptitle("Kyber (ML-KEM-512): Benchmark Comparison", fontsize=15, fontweight="bold")

    blue, green = "#1f77b4", "#2ca02c"

    def bar2(ax, title, labels, values, colors):
        ax.bar(labels, values, color=colors)
        ax.set_title(title, fontweight="bold")
        ax.grid(axis="y", linestyle="--", alpha=0.6)

    bar2(axs[0, 0], "Auth/KEM time (s)",  ["Traditional", "ML-KEM"], [trad_sign, kem_time],       [blue, green])
    bar2(axs[0, 1], "Send+confirm (s)",   ["Traditional", "ML-KEM"], [trad_confirm, kem_confirm],  [blue, green])
    bar2(axs[0, 2], "Gas used",           ["Traditional", "ML-KEM"], [trad_gas, kem_gas],           [blue, green])
    bar2(axs[0, 3], "Crypto bytes",       ["Traditional", "ML-KEM"], [trad_bytes, kem_bytes],       [blue, green])

    bar2(axs[1, 0], "AES time (s)",       ["Encrypt", "Decrypt"],    [aes_enc, aes_dec],            [green, green])
    bar2(axs[1, 1], "Payload size",       ["Plaintext", "Encrypted"], [plain_size, enc_size],     [green, green])

    if has_ipfs:
        bar2(axs[1, 2], "IPFS Upload (s)", ["Ciphertext", "Pubkey"], [ipfs_ct_up, ipfs_pk_up], [green, green])
    else:
        axs[1, 2].axis("off")

    if has_e2e:
        axs[1, 3].bar(["Download", "Hash", "Decaps", "AES"], [ct_dl, hash_cmp, kem_decaps, aes_dec_e2e], color=[green]*4)
        axs[1, 3].set_title("E2E Latency Breakdown (s)", fontweight="bold")
        axs[1, 3].grid(axis="y", linestyle="--", alpha=0.6)
        # xoay label nếu cần
        for tick in axs[1, 3].get_xticklabels():
            tick.set_rotation(15)
    else:
        axs[1, 3].axis("off")

    plt.tight_layout()
    plt.savefig(OUTPUT_PLOT, dpi=150)
    plt.close()
    return OUTPUT_PLOT, OUTPUT_MD


def main() -> None:
    traditional = load_result(TRADITIONAL_RESULT)
    kem         = load_result(KEM_RESULT)
    e2e         = load_result(E2E_RESULT) if E2E_RESULT.exists() else None
    print_summary(traditional, kem, e2e)
    plot_path, md_path = save_plot_and_md(traditional, kem, e2e)
    print(f"Plot saved     : {plot_path}")
    print(f"Markdown saved : {md_path}")


if __name__ == "__main__":
    main()
