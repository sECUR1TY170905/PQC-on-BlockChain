"""Compare benchmark outputs from traditional and PQC demo runs."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt


RESULTS_DIR = Path(__file__).resolve().parent / "results"
p = Path(__file__).resolve()
if "dilithium" in str(p):
    TRADITIONAL_RESULT = RESULTS_DIR / "traditional_result.json"
else:
    TRADITIONAL_RESULT = p.parents[2] / "dilithium" / "benchmark" / "results" / "traditional_result.json"

PQC_RESULT = RESULTS_DIR / "pqc_result.json"
E2E_RESULT = RESULTS_DIR / "verify_e2e_result.json"
OUTPUT_PLOT = RESULTS_DIR / "comparison.png"


def load_result(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing result file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def print_summary(traditional: dict, pqc: dict, e2e: dict | None) -> None:
    algo_name = pqc["pqc"]["algorithm"]
    print(f"=== {algo_name} Comparison Summary ===")
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


def save_plot(traditional: dict, pqc: dict, e2e: dict | None) -> Path:
    has_ipfs = "signature_upload_seconds" in pqc["benchmark"]
    has_e2e = e2e is not None
    algo_name = pqc["pqc"]["algorithm"]

    trad_sign    = traditional["benchmark"]["ecdsa_sign_seconds"]
    pqc_sign     = pqc["benchmark"]["pqc_sign_seconds"] + pqc["benchmark"]["pqc_verify_seconds"]
    trad_confirm = traditional["benchmark"]["send_and_confirm_seconds"]
    pqc_confirm  = pqc["benchmark"]["send_and_confirm_seconds"]
    trad_gas     = traditional["gas_used"]
    pqc_gas      = pqc["gas_used"]
    trad_bytes   = traditional["benchmark"]["signature_size_bytes"]
    pqc_bytes    = pqc["pqc"]["signature_size_bytes"]

    ipfs_sig_up = pqc["benchmark"].get("signature_upload_seconds", 0)
    ipfs_pk_up  = pqc["benchmark"].get("public_key_upload_seconds", 0)

    e2e_latency = e2e["benchmark"]["e2e_verification_latency"] if has_e2e else None
    sig_dl      = e2e["benchmark"]["signature_download_seconds"] if has_e2e else None
    pk_dl       = e2e["benchmark"]["public_key_download_seconds"] if has_e2e else None
    hash_cmp    = e2e["benchmark"]["hash_comparison_seconds"] if has_e2e else None
    pqc_ver     = e2e["benchmark"]["pqc_verify_seconds"] if has_e2e else None

    # --- 6 subplots (2x3) ---
    fig, axs = plt.subplots(2, 3, figsize=(15, 8))
    fig.suptitle(f"{algo_name}: Benchmark Comparison", fontsize=15, fontweight="bold")

    blue, orange = "#1f77b4", "#ff7f0e"

    def bar2(ax, title, labels, values, colors):
        ax.bar(labels, values, color=colors)
        ax.set_title(title, fontweight="bold")
        ax.grid(axis="y", linestyle="--", alpha=0.6)

    bar2(axs[0, 0], "Signing time (s)",  ["Traditional", "PQC"], [trad_sign, pqc_sign],      [blue, orange])
    bar2(axs[0, 1], "Send+confirm (s)",  ["Traditional", "PQC"], [trad_confirm, pqc_confirm], [blue, orange])
    bar2(axs[0, 2], "Gas used",          ["Traditional", "PQC"], [trad_gas, pqc_gas],          [blue, orange])
    bar2(axs[1, 0], "Auth bytes",        ["Traditional", "PQC"], [trad_bytes, pqc_bytes],      [blue, orange])

    if has_ipfs:
        bar2(axs[1, 1], "IPFS Upload (s)", ["Signature", "Pubkey"], [ipfs_sig_up, ipfs_pk_up], [orange, orange])
    else:
        axs[1, 1].axis("off")

    if has_e2e:
        axs[1, 2].bar(["Sig DL", "PK DL", "Hash", "PQC Ver"], [sig_dl, pk_dl, hash_cmp, pqc_ver], color=[orange]*4)
        axs[1, 2].set_title("E2E Latency Breakdown (s)", fontweight="bold")
        axs[1, 2].grid(axis="y", linestyle="--", alpha=0.6)
        for tick in axs[1, 2].get_xticklabels():
            tick.set_rotation(15)
    else:
        axs[1, 2].axis("off")

    plt.tight_layout()
    plt.savefig(OUTPUT_PLOT, dpi=150)
    plt.close()
    return OUTPUT_PLOT


def main() -> None:
    traditional = load_result(TRADITIONAL_RESULT)
    pqc         = load_result(PQC_RESULT)
    e2e         = load_result(E2E_RESULT) if E2E_RESULT.exists() else None
    print_summary(traditional, pqc, e2e)
    plot_path = save_plot(traditional, pqc, e2e)
    print(f"Plot saved     : {plot_path}")


if __name__ == "__main__":
    main()
