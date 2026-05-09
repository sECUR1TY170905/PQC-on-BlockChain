"""Compare benchmark outputs from traditional and PQC demo runs."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt


RESULTS_DIR = Path(__file__).resolve().parent / "results"
TRADITIONAL_RESULT = RESULTS_DIR / "traditional_result.json"
PQC_RESULT = RESULTS_DIR / "pqc_result.json"
OUTPUT_PLOT = RESULTS_DIR / "comparison.png"
OUTPUT_MD = RESULTS_DIR / "comparison_summary.md"


def load_result(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing result file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def print_summary(traditional: dict, pqc: dict) -> None:
    print("Comparison Summary")
    print(f"Traditional tx hash: {traditional['tx_hash']}")
    print(f"PQC tx hash: {pqc['tx_hash']}")
    print(f"Traditional gas used: {traditional['gas_used']}")
    print(f"PQC gas used: {pqc['gas_used']}")
    print(
        "Traditional signing time: "
        f"{traditional['benchmark']['ecdsa_sign_seconds']} s"
    )
    print(f"PQC sign time: {pqc['benchmark']['pqc_sign_seconds']} s")
    print(f"PQC verify time: {pqc['benchmark']['pqc_verify_seconds']} s")
    print(f"PQC signature size: {pqc['pqc']['signature_size_bytes']} bytes")


def save_plot_and_md(traditional: dict, pqc: dict) -> tuple[Path, Path]:
    labels = [
        "Signing time (s)",
        "Send+confirm (s)",
        "Gas used",
        "Auth bytes",
    ]
    traditional_values = [
        traditional["benchmark"]["ecdsa_sign_seconds"],
        traditional["benchmark"]["send_and_confirm_seconds"],
        traditional["gas_used"],
        traditional["benchmark"]["signature_size_bytes"],
    ]
    pqc_values = [
        pqc["benchmark"]["pqc_sign_seconds"] + pqc["benchmark"]["pqc_verify_seconds"],
        pqc["benchmark"]["send_and_confirm_seconds"],
        pqc["gas_used"],
        pqc["pqc"]["signature_size_bytes"],
    ]

    # 1. Xuất ra file Markdown
    md_lines = [
        "# Traditional vs PQC Comparison",
        "",
        "| Metric | Traditional (ECDSA) | PQC Hybrid |",
        "|---|---|---|",
    ]
    for i in range(4):
        # Format số thập phân cho thời gian
        val_trad = f"{traditional_values[i]:.6f}" if isinstance(traditional_values[i], float) else traditional_values[i]
        val_pqc = f"{pqc_values[i]:.6f}" if isinstance(pqc_values[i], float) else pqc_values[i]
        md_lines.append(f"| **{labels[i]}** | {val_trad} | {val_pqc} |")
    
    OUTPUT_MD.write_text("\\n".join(md_lines), encoding="utf-8")

    # 2. Chia thành 4 biểu đồ con (Subplots)
    fig, axs = plt.subplots(2, 2, figsize=(10, 8))
    fig.suptitle("Traditional vs PQC Hybrid", fontsize=16)
    
    for i, ax in enumerate(axs.flat):
        ax.bar(["Traditional", "PQC Hybrid"], [traditional_values[i], pqc_values[i]], color=["#1f77b4", "#ff7f0e"])
        ax.set_title(labels[i], fontweight='bold')
        ax.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.savefig(OUTPUT_PLOT)
    plt.close()
    
    return OUTPUT_PLOT, OUTPUT_MD


def main() -> None:
    traditional = load_result(TRADITIONAL_RESULT)
    pqc = load_result(PQC_RESULT)
    print_summary(traditional, pqc)
    plot_path, md_path = save_plot_and_md(traditional, pqc)
    print(f"Plot saved to: {plot_path}")
    print(f"Markdown report saved to: {md_path}")


if __name__ == "__main__":
    main()
