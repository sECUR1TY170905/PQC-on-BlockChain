"""Compare benchmark outputs from traditional and PQC demo runs (with IPFS + E2E metrics)."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt


RESULTS_DIR = Path(__file__).resolve().parent / "results"
TRADITIONAL_RESULT = RESULTS_DIR / "traditional_result.json"
PQC_RESULT = RESULTS_DIR / "pqc_result.json"
E2E_RESULT = RESULTS_DIR / "verify_e2e_result.json"
OUTPUT_PLOT = RESULTS_DIR / "comparison.png"
OUTPUT_MD = RESULTS_DIR / "comparison_summary.md"


def load_result(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing result file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def print_summary(traditional: dict, pqc: dict, e2e: dict | None) -> None:
    print("=== Dilithium (ML-DSA-44) Comparison Summary ===")
    print(f"  Traditional gas used   : {traditional['gas_used']}")
    print(f"  PQC gas used           : {pqc['gas_used']}")
    print(f"  Traditional sign time  : {traditional['benchmark']['ecdsa_sign_seconds']} s")
    print(f"  PQC sign time          : {pqc['benchmark']['pqc_sign_seconds']} s")
    print(f"  PQC verify time        : {pqc['benchmark']['pqc_verify_seconds']} s")
    print(f"  PQC signature size     : {pqc['pqc']['signature_size_bytes']} bytes")
    if "signature_upload_seconds" in pqc["benchmark"]:
        print(f"  IPFS sig upload        : {pqc['benchmark']['signature_upload_seconds']} s")
        print(f"  IPFS pubkey upload     : {pqc['benchmark']['public_key_upload_seconds']} s")
    if e2e:
        print(f"  E2E latency            : {e2e['benchmark']['e2e_verification_latency']} s")
        print(f"  Verification passed    : {e2e['verification_passed']}")


def save_plot_and_md(traditional: dict, pqc: dict, e2e: dict | None) -> tuple[Path, Path]:
    # --- Chuẩn bị dữ liệu ---
    has_ipfs = "signature_upload_seconds" in pqc["benchmark"]
    has_e2e = e2e is not None

    trad_sign   = traditional["benchmark"]["ecdsa_sign_seconds"]
    pqc_sign    = pqc["benchmark"]["pqc_sign_seconds"] + pqc["benchmark"]["pqc_verify_seconds"]
    trad_confirm = traditional["benchmark"]["send_and_confirm_seconds"]
    pqc_confirm  = pqc["benchmark"]["send_and_confirm_seconds"]
    trad_gas    = traditional["gas_used"]
    pqc_gas     = pqc["gas_used"]
    trad_bytes  = traditional["benchmark"]["signature_size_bytes"]
    pqc_bytes   = pqc["pqc"]["signature_size_bytes"]

    ipfs_sig_up = pqc["benchmark"].get("signature_upload_seconds", 0)
    ipfs_pk_up  = pqc["benchmark"].get("public_key_upload_seconds", 0)

    e2e_latency  = e2e["benchmark"]["e2e_verification_latency"]  if has_e2e else None
    sig_dl       = e2e["benchmark"]["signature_download_seconds"] if has_e2e else None
    pk_dl        = e2e["benchmark"]["public_key_download_seconds"] if has_e2e else None
    hash_cmp     = e2e["benchmark"]["hash_comparison_seconds"]    if has_e2e else None
    pqc_verify   = e2e["benchmark"]["pqc_verify_seconds"]         if has_e2e else None

    # ------------------------------------------------------------------
    # 1. Xuất Markdown
    # ------------------------------------------------------------------
    md = []
    md += [
        "# Dilithium (ML-DSA-44) — Comparison Summary",
        "",
        "## A. Traditional vs PQC Hybrid",
        "",
        "| Metric | Traditional (ECDSA) | PQC Hybrid (Dilithium) |",
        "|---|---:|---:|",
        f"| **Signing time (s)**  | {trad_sign:.6f}  | {pqc_sign:.6f}  |",
        f"| **Send+confirm (s)**  | {trad_confirm:.6f}  | {pqc_confirm:.6f}  |",
        f"| **Gas used**          | {trad_gas}       | {pqc_gas}       |",
        f"| **Auth bytes**        | {trad_bytes}     | {pqc_bytes}     |",
    ]

    if has_ipfs:
        md += [
            "",
            "## B. IPFS Off-chain Upload (Sender side)",
            "",
            "| Metric | Value |",
            "|---|---:|",
            f"| **Signature upload (s)**  | {ipfs_sig_up:.6f} |",
            f"| **Public key upload (s)** | {ipfs_pk_up:.6f} |",
            f"| **Total upload (s)**      | {ipfs_sig_up + ipfs_pk_up:.6f} |",
        ]

    if has_e2e:
        md += [
            "",
            "## C. End-to-End Verification (Receiver side)",
            "",
            "| Metric | Value |",
            "|---|---:|",
            f"| **Signature download (s)**  | {sig_dl:.6f} |",
            f"| **Public key download (s)** | {pk_dl:.6f} |",
            f"| **Hash comparison (s)**     | {hash_cmp:.6f} |",
            f"| **PQC verify (s)**          | {pqc_verify:.6f} |",
            f"| **E2E latency (s)**         | {e2e_latency:.6f} |",
            f"| **Verification passed**     | {e2e['verification_passed']} |",
        ]

    OUTPUT_MD.write_text("\n".join(md), encoding="utf-8")

    # ------------------------------------------------------------------
    # 2. Vẽ biểu đồ — 2 hàng x 3 cột (6 subplots)
    # ------------------------------------------------------------------
    fig, axs = plt.subplots(2, 3, figsize=(15, 8))
    fig.suptitle("Dilithium (ML-DSA-44): Benchmark Comparison", fontsize=15, fontweight="bold")

    blue, orange, green = "#1f77b4", "#ff7f0e", "#2ca02c"

    def bar2(ax, title, left_label, right_label, left_val, right_val, left_color, right_color):
        ax.bar([left_label, right_label], [left_val, right_val], color=[left_color, right_color])
        ax.set_title(title, fontweight="bold")
        ax.grid(axis="y", linestyle="--", alpha=0.6)

    # Hàng 1: 4 chỉ số so sánh truyền thống vs PQC
    bar2(axs[0, 0], "Signing time (s)",
         "Traditional", "PQC", trad_sign, pqc_sign, blue, orange)

    bar2(axs[0, 1], "Send+confirm (s)",
         "Traditional", "PQC", trad_confirm, pqc_confirm, blue, orange)

    bar2(axs[0, 2], "Gas used",
         "Traditional", "PQC", trad_gas, pqc_gas, blue, orange)

    bar2(axs[1, 0], "Auth bytes",
         "Traditional", "PQC", trad_bytes, pqc_bytes, blue, orange)

    # Hàng 2: IPFS upload
    if has_ipfs:
        axs[1, 1].bar(["Sig upload", "PK upload"], [ipfs_sig_up, ipfs_pk_up], color=[green, green])
        axs[1, 1].set_title("IPFS Upload (s)", fontweight="bold")
        axs[1, 1].grid(axis="y", linestyle="--", alpha=0.6)
    else:
        axs[1, 1].axis("off")

    # Hàng 2: E2E latency breakdown
    if has_e2e:
        axs[1, 2].bar(
            ["Download", "Hash cmp", "PQC verify"],
            [sig_dl + pk_dl, hash_cmp, pqc_verify],
            color=[green, green, green],
        )
        axs[1, 2].set_title("E2E Latency Breakdown (s)", fontweight="bold")
        axs[1, 2].grid(axis="y", linestyle="--", alpha=0.6)
    else:
        axs[1, 2].axis("off")

    plt.tight_layout()
    plt.savefig(OUTPUT_PLOT, dpi=150)
    plt.close()

    return OUTPUT_PLOT, OUTPUT_MD


def main() -> None:
    traditional = load_result(TRADITIONAL_RESULT)
    pqc         = load_result(PQC_RESULT)
    e2e         = load_result(E2E_RESULT) if E2E_RESULT.exists() else None

    print_summary(traditional, pqc, e2e)
    plot_path, md_path = save_plot_and_md(traditional, pqc, e2e)
    print(f"Plot saved     : {plot_path}")
    print(f"Markdown saved : {md_path}")


if __name__ == "__main__":
    main()
