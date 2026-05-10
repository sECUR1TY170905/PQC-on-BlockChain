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
    print("=== SPHINCS+ (sphincs_sha2_128f_simple) Comparison Summary ===")
    print(f"  Traditional gas used   : {traditional['gas_used']}")
    print(f"  PQC gas used           : {pqc['gas_used']}")
    print(f"  Traditional sign time  : {traditional['benchmark']['ecdsa_sign_seconds']} s")
    print(f"  PQC sign time          : {pqc['benchmark']['pqc_sign_seconds']} s")
    print(f"  PQC verify time        : {pqc['benchmark']['pqc_verify_seconds']} s")
    print(f"  PQC signature size     : {pqc['pqc']['signature_size_bytes']} bytes")


def save_plot_and_md(traditional: dict, pqc: dict) -> tuple[Path, Path]:
    trad_sign    = traditional["benchmark"]["ecdsa_sign_seconds"]
    pqc_sign     = pqc["benchmark"]["pqc_sign_seconds"] + pqc["benchmark"]["pqc_verify_seconds"]
    trad_confirm = traditional["benchmark"]["send_and_confirm_seconds"]
    pqc_confirm  = pqc["benchmark"]["send_and_confirm_seconds"]
    trad_gas     = traditional["gas_used"]
    pqc_gas      = pqc["gas_used"]
    trad_bytes   = traditional["benchmark"]["signature_size_bytes"]
    pqc_bytes    = pqc["pqc"]["signature_size_bytes"]

    # --- Markdown ---
    md = [
        "# SPHINCS+ (sphincs_sha2_128f_simple) — Comparison Summary",
        "",
        "## A. Traditional vs PQC Hybrid",
        "",
        "| Metric | Traditional (ECDSA) | PQC Hybrid (SPHINCS+) |",
        "|---|---:|---:|",
        f"| **Signing time (s)**  | {trad_sign:.6f}  | {pqc_sign:.6f}  |",
        f"| **Send+confirm (s)**  | {trad_confirm:.6f}  | {pqc_confirm:.6f}  |",
        f"| **Gas used**          | {trad_gas}       | {pqc_gas}       |",
        f"| **Auth bytes**        | {trad_bytes}     | {pqc_bytes}     |",
        "",
        "> **Lưu ý:** SPHINCS+ chưa được cập nhật lên contract mới (chưa có IPFS/E2E metrics).",
    ]
    OUTPUT_MD.write_text("\n".join(md), encoding="utf-8")

    # --- 4 subplots (2x2) ---
    fig, axs = plt.subplots(2, 2, figsize=(10, 8))
    fig.suptitle("SPHINCS+ (sphincs_sha2_128f_simple): Benchmark Comparison", fontsize=14, fontweight="bold")

    blue, orange = "#1f77b4", "#ff7f0e"

    def bar2(ax, title, labels, values, colors):
        ax.bar(labels, values, color=colors)
        ax.set_title(title, fontweight="bold")
        ax.grid(axis="y", linestyle="--", alpha=0.6)

    bar2(axs[0, 0], "Signing time (s)",  ["Traditional", "PQC"], [trad_sign, pqc_sign],      [blue, orange])
    bar2(axs[0, 1], "Send+confirm (s)",  ["Traditional", "PQC"], [trad_confirm, pqc_confirm], [blue, orange])
    bar2(axs[1, 0], "Gas used",          ["Traditional", "PQC"], [trad_gas, pqc_gas],          [blue, orange])
    bar2(axs[1, 1], "Auth bytes",        ["Traditional", "PQC"], [trad_bytes, pqc_bytes],      [blue, orange])

    plt.tight_layout()
    plt.savefig(OUTPUT_PLOT, dpi=150)
    plt.close()
    return OUTPUT_PLOT, OUTPUT_MD


def main() -> None:
    traditional = load_result(TRADITIONAL_RESULT)
    pqc         = load_result(PQC_RESULT)
    print_summary(traditional, pqc)
    plot_path, md_path = save_plot_and_md(traditional, pqc)
    print(f"Plot saved     : {plot_path}")
    print(f"Markdown saved : {md_path}")


if __name__ == "__main__":
    main()
