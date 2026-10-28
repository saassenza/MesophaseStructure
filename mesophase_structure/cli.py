"""Command-line interface.

Single sample:
    python -m mesophase_structure --phase Pn3m --lattice 8.57 --water 36 --density 1.05

Batch (CSV with columns phase,lattice,water,density; results written as CSV):
    python -m mesophase_structure --csv examples/samples.csv > results.csv
"""

import argparse
import csv
import sys

from .core import PHASES, structure

FIELDS = ["phase", "lattice_nm", "water_wt_percent", "lipid_density_g_cm3",
          "water_volume_fraction", "radius_nm", "water_thickness_nm",
          "lipid_length_nm", "lipid_length_average_nm"]


def _row(res, water, density):
    def f(v):
        return "" if v is None else "%.6g" % v
    return [res.phase, f(res.lattice), f(water), f(density), f(res.water_volume_fraction),
            f(res.radius), f(res.water_thickness), f(res.lipid_length),
            f(res.lipid_length_average)]


def _print_single(res):
    print("Phase:                  %s" % res.phase)
    print("Water volume fraction:  %.4f" % res.water_volume_fraction)
    if res.phase == "La":
        print("Water lamellae (nm):    %.4f" % res.water_thickness)
        print("Lipid length (nm):      %.4f" % res.lipid_length)
    elif res.phase == "Hex":
        print("Channel radius (nm):    %.4f" % res.radius)
        print("Lipid length L_unf (nm): %.4f" % res.lipid_length)
        print("Lipid length L_ave (nm): %.4f" % res.lipid_length_average)
    else:
        print("Channel radius (nm):    %.4f" % res.radius)
        print("Lipid length (nm):      %.4f" % res.lipid_length)


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="mesophase-structure",
        description="Structural parameters of lipid mesophases from the SAXS lattice parameter.")
    ap.add_argument("--phase", choices=PHASES, help="mesophase symmetry")
    ap.add_argument("--lattice", type=float, help="lattice parameter (nm)")
    ap.add_argument("--water", type=float, help="water content (%% weight)")
    ap.add_argument("--density", type=float, help="lipid density (g/cm^3)")
    ap.add_argument("--csv", metavar="FILE",
                    help="batch mode: CSV file with columns phase,lattice,water,density")
    args = ap.parse_args(argv)

    try:
        if args.csv:
            out = csv.writer(sys.stdout)
            out.writerow(FIELDS)
            with open(args.csv, newline="") as fh:
                for rec in csv.DictReader(fh):
                    water, density = float(rec["water"]), float(rec["density"])
                    res = structure(rec["phase"].strip(), float(rec["lattice"]), water, density)
                    out.writerow(_row(res, water, density))
        else:
            if None in (args.phase, args.lattice, args.water, args.density):
                ap.error("--phase, --lattice, --water and --density are required (or use --csv)")
            _print_single(structure(args.phase, args.lattice, args.water, args.density))
    except ValueError as err:
        sys.exit("Error: %s" % err)


if __name__ == "__main__":
    main()
