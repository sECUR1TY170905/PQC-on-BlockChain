"""Compare traditional baseline against ML-KEM confidentiality results."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt


RESULTS_DIR = Path(__file__).resolve().parent / "results"
TRADITIONAL_RESULT = RESULTS_DIR / "traditional_result.json"
KEM_RESULT = RESULTS_DIR / "kyber_confidentiality_result.json"
OUTPUT_PLOT = RESULTS_DIR / "comparison_kem.png"
OUTPUT_MD = RESULTS_DIR / "comparison_kem_summary.md"


def load_result(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing result file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def print_summary(traditional: dict, kem_result: dict) -> None:
    print("Comparison Summary")
    print(f"Traditional tx hash: {traditional['tx_hash']}")
    print(f"ML-KEM tx hash: {kem_result['tx_hash']}")
    print(f"Traditional gas used: {traditional['gas_used']}")
    print(f"ML-KEM gas used: {kem_result['gas_used']}")
    print(f"Traditional signing time: {traditional['benchmark']['ecdsa_sign_seconds']} s")
    print(f"ML-KEM encaps time: {kem_result['benchmark']['kem_encaps_seconds']} s")
    print(f"ML-KEM decaps time: {kem_result['benchmark']['kem_decaps_seconds']} s")
    print(f"ML-KEM ciphertext size: {kem_result['kem']['ciphertext_size_bytes']} bytes")


def save_plot_and_md(traditional: dict, kem_result: dict) -> tuple[Path, Path]:
    labels = [
        "Auth/KEM time (s)",
        "Send+confirm (s)",
        "Gas used",
        "Crypto bytes",
    ]
    traditional_values = [
        traditional["benchmark"]["ecdsa_sign_seconds"],
        traditional["benchmark"]["send_and_confirm_seconds"],
        traditional["gas_used"],
        traditional["benchmark"]["signature_size_bytes"],
    ]
    kem_values = [
        kem_result["benchmark"]["kem_encaps_seconds"] + kem_result["benchmark"]["kem_decaps_seconds"],
        kem_result["benchmark"]["send_and_confirm_seconds"],
        kem_result["gas_used"],
        kem_result["kem"]["ciphertext_size_bytes"],
    ]

    # 1. Xuất ra file Markdown
    md_lines = [
        "# Traditional vs ML-KEM Comparison",
        "",
        "| Metric | Traditional (ECDSA) | ML-KEM Confidential |",
        "|---|---|---|",
    ]
    for i in range(4):
        # Format số thập phân cho thời gian
        val_trad = f"{traditional_values[i]:.6f}" if isinstance(traditional_values[i], float) else traditional_values[i]
        val_kem = f"{kem_values[i]:.6f}" if isinstance(kem_values[i], float) else kem_values[i]
        md_lines.append(f"| **{labels[i]}** | {val_trad} | {val_kem} |")
    
    OUTPUT_MD.write_text("\\n".join(md_lines), encoding="utf-8")

    # 2. Chia thành 4 biểu đồ con (Subplots)
    fig, axs = plt.subplots(2, 2, figsize=(10, 8))
    fig.suptitle("Traditional vs ML-KEM Confidentiality", fontsize=16)
    
    for i, ax in enumerate(axs.flat):
        ax.bar(["Traditional", "ML-KEM"], [traditional_values[i], kem_values[i]], color=["#1f77b4", "#2ca02c"])
        ax.set_title(labels[i], fontweight='bold')
        ax.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.savefig(OUTPUT_PLOT)
    plt.close()
    
    return OUTPUT_PLOT, OUTPUT_MD


def main() -> None:
    traditional = load_result(TRADITIONAL_RESULT)
    kem_result = load_result(KEM_RESULT)
    print_summary(traditional, kem_result)
    plot_path, md_path = save_plot_and_md(traditional, kem_result)
    print(f"Plot saved to: {plot_path}")
    print(f"Markdown report saved to: {md_path}")


if __name__ == "__main__":
    main()
