"""Fit nonnegative diagonal steady-tow drag from measured CSV, not from simulation."""

from pathlib import Path
import argparse, csv, hashlib, json
import numpy as np


def fit_drag(path):
    with Path(path).open() as f:
        rows = list(csv.DictReader(f))
    coefficients = []
    metrics = []
    for axis in "xyz":
        v = np.array([float(r["velocity_" + axis + "_m_s"]) for r in rows])
        force = np.array([float(r["drag_" + axis + "_N"]) for r in rows])
        keep = np.abs(v) > 1e-6
        v = v[keep]
        force = force[keep]
        if len(v) < 6 or not np.isfinite(v).all() or not np.isfinite(force).all():
            raise ValueError("Need >=6 finite nonzero velocity/drag samples per axis")
        A = np.c_[v, np.abs(v) * v]
        b = -force
        if np.linalg.matrix_rank(A) < 2:
            raise ValueError("Need multiple distinct speed magnitudes on axis " + axis)
        candidates = [
            np.maximum(np.linalg.lstsq(A, b, rcond=None)[0], 0),
            np.array([max(0, float(A[:, 0] @ b / (A[:, 0] @ A[:, 0]))), 0]),
            np.array([0, max(0, float(A[:, 1] @ b / (A[:, 1] @ A[:, 1])))]),
            np.zeros(2),
        ]
        coef = min(candidates, key=lambda c: np.linalg.norm(A @ c - b))
        prediction = -A @ coef
        coefficients.append(coef)
        metrics.append(
            {
                "axis": axis,
                "samples": len(v),
                "RMSE_N": float(np.sqrt(np.mean((prediction - force) ** 2))),
            }
        )
    c = np.array(coefficients)
    return {
        "overrides": {
            "assumed_linear_drag": c[:, 0].tolist(),
            "assumed_quadratic_drag": c[:, 1].tolist(),
        },
        "fit_metrics": metrics,
        "input_sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest(),
        "model": "F_drag = -linear*v_relative - quadratic*abs(v_relative)*v_relative, body axes, SI",
        "measurement_validity": "User must verify steady tow, offsets, alignment, sensor calibration and separation of other loads. A numerical fit is not physical validation.",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("csv", type=Path)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    report = fit_drag(a.csv)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
