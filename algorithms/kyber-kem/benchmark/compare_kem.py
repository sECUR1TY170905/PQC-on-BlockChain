"""Compare traditional baseline against ML-KEM confidentiality results."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt


RESULTS_DIR = Path(__file__).resolve().parent / "results"
TRADITIONAL_RESULT = Path(__file__).resolve().parents[2] / "dilithium" / "benchmark" / "results" / "traditional_result.json"
KEM_RESULT = RESULTS_DIR / "kyber_confidentiality_result.json"
OUTPUT_PLOT = RESULTS_DIR / "comparison_kem.png"


def load_result(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing result file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def print_summary(traditional: dict, kem: dict) -> None:
    print("=== Kyber (ML-KEM-512) Comparison Summary ===")
    print(f"  Traditional gas used   : {traditional['gas_used']}")
    print(f"  ML-KEM gas used        : {kem['gas_used']}")
    print(f"  Traditional sign time  : {traditional['benchmark']['ecdsa_sign_seconds']} s")
    print(f"  ML-KEM encaps time     : {kem['benchmark']['kem_encaps_seconds']} s")
    print(f"  ML-KEM decaps time     : {kem['benchmark']['kem_decaps_seconds']} s")
    print(f"  ML-KEM ciphertext size : {kem['kem']['ciphertext_size_bytes']} bytes")
    print(f"  AES encrypt time       : {kem['confidentiality']['encryption_seconds']} s")
    print(f"  AES decrypt time       : {kem['confidentiality']['decrypt_seconds']} s")


def save_plot(traditional: dict, kem: dict) -> Path:
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

    # --- 6 subplots (2x3) ---
    fig, axs = plt.subplots(2, 3, figsize=(15, 8))
    fig.suptitle("Kyber (ML-KEM-512): Benchmark Comparison", fontsize=15, fontweight="bold")

    blue, green = "#1f77b4", "#2ca02c"

    def bar2(ax, title, labels, values, colors):
        ax.bar(labels, values, color=colors)
        ax.set_title(title, fontweight="bold")
        ax.grid(axis="y", linestyle="--", alpha=0.6)

    bar2(axs[0, 0], "Auth/KEM time (s)",  ["Traditional", "ML-KEM"], [trad_sign, kem_time],       [blue, green])
    bar2(axs[0, 1], "Send+confirm (s)",   ["Traditional", "ML-KEM"], [trad_confirm, kem_confirm],  [blue, green])
    bar2(axs[0, 2], "Gas used",           ["Traditional", "ML-KEM"], [trad_gas, kem_gas],           [blue, green])
    bar2(axs[1, 0], "Crypto bytes",       ["Traditional", "ML-KEM"], [trad_bytes, kem_bytes],       [blue, green])
    bar2(axs[1, 1], "AES time (s)",       ["Encrypt", "Decrypt"],    [aes_enc, aes_dec],            [green, green])
    bar2(axs[1, 2], "Payload size (bytes)", ["Plaintext", "Encrypted"], [plain_size, enc_size],     [green, green])

    plt.tight_layout()
    plt.savefig(OUTPUT_PLOT, dpi=150)
    plt.close()
    return OUTPUT_PLOT


def main() -> None:
    traditional = load_result(TRADITIONAL_RESULT)
    kem         = load_result(KEM_RESULT)
    print_summary(traditional, kem)
    plot_path = save_plot(traditional, kem)
    print(f"Plot saved     : {plot_path}")


if __name__ == "__main__":
    main()
