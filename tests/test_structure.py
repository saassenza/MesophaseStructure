"""Tests: reference values reproduce the online tool at https://www.salvatoreassenza.com/#tools.

Run with:  python -m unittest discover tests
"""

import math
import subprocess
import sys
import unittest
from pathlib import Path

from mesophase_structure import PHASES, structure, water_volume_fraction

ROOT = Path(__file__).resolve().parents[1]

# lattice 8.57 nm, 36 % weight water, lipid density 1.05 g/cm^3
REFERENCE = {
    "Pn3m": dict(radius=1.8438344477024582, lipid_length=1.5051519012178243),
    "Im3m": dict(radius=1.3757997614619037, lipid_length=1.2419752371457842),
    "Ia3d": dict(radius=1.194065880639083, lipid_length=0.9311125370984674),
    "Hex": dict(radius=2.7418469723906282, lipid_length=1.543153027609372,
                lipid_length_average=1.7535356338460701),
    "La": dict(water_thickness=3.1821807465618863, lipid_length=2.693909626719057),
}


class TestStructure(unittest.TestCase):
    def test_reference_values(self):
        for phase, ref in REFERENCE.items():
            res = structure(phase, 8.57, 36, 1.05)
            for key, value in ref.items():
                self.assertAlmostEqual(getattr(res, key), value, places=12, msg=(phase, key))

    def test_cubic_volume_balance(self):
        # lipid volume fraction = 2 A0 (L/a) + 4/3 pi chi (L/a)^3
        from mesophase_structure import CUBIC_GEOMETRY
        for phase, (a0, chi) in CUBIC_GEOMETRY.items():
            res = structure(phase, 10.0, 30, 1.0)
            x = res.lipid_length / res.lattice
            self.assertAlmostEqual(2 * a0 * x + 4 / 3 * math.pi * chi * x ** 3,
                                   res.lipid_volume_fraction, places=12)

    def test_lamellar_sums_to_lattice(self):
        res = structure("La", 5.0, 25, 1.0)
        self.assertAlmostEqual(res.water_thickness + 2 * res.lipid_length, 5.0, places=12)

    def test_water_volume_fraction(self):
        self.assertAlmostEqual(water_volume_fraction(50, 1.0), 0.5, places=12)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            structure("Fd3m", 8, 30, 1)
        with self.assertRaises(ValueError):
            structure("Pn3m", -1, 30, 1)
        with self.assertRaises(ValueError):
            structure("Pn3m", 8, 100, 1)

    def test_cli(self):
        for phase in PHASES:
            out = subprocess.run([sys.executable, "-m", "mesophase_structure", "--phase", phase,
                                  "--lattice", "8.57", "--water", "36", "--density", "1.05"],
                                 cwd=ROOT, capture_output=True, text=True, check=True).stdout
            self.assertIn("Lipid length", out)

    def test_cli_csv(self):
        out = subprocess.run([sys.executable, "-m", "mesophase_structure", "--csv",
                              "examples/samples.csv"],
                             cwd=ROOT, capture_output=True, text=True, check=True).stdout
        self.assertEqual(len(out.strip().splitlines()), 1 + 5)


if __name__ == "__main__":
    unittest.main()
