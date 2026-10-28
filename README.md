# MesophaseStructure

Structural parameters of lipid mesophases from their SAXS lattice parameter: the radius of the water channels, the thickness of the water lamellae and the lipid length. It covers bicontinuous cubic phases (Pn3m, Im3m, Ia3d), the inverse hexagonal phase (Hex) and the lamellar phase (Lα).

Pure Python (≥ 3.8), no dependencies.

## Installation

```bash
pip install git+https://github.com/saassenza/MesophaseStructure
```

or simply download the repository and run it from its folder (`python -m mesophase_structure ...`).

## Usage

### Command line

```bash
mesophase-structure --phase Pn3m --lattice 8.57 --water 36 --density 1.05
```

```
Phase:                  Pn3m
Water volume fraction:  0.3713
Channel radius (nm):    1.8438
Lipid length (nm):      1.5052
```

Batch mode: a CSV file with columns `phase,lattice,water,density` (see `examples/samples.csv`):

```bash
mesophase-structure --csv examples/samples.csv > results.csv
```

If the package is not installed, replace `mesophase-structure` with `python -m mesophase_structure`.

### Python

```python
from mesophase_structure import structure

res = structure("Pn3m", lattice=8.57, water_weight=36, lipid_density=1.05)
print(res.radius, res.lipid_length)
```

`structure()` returns a `StructureResult` with fields `radius` (cubic and Hex), `water_thickness` (Lα), `lipid_length` (L<sub>unf</sub> for Hex), `lipid_length_average` (Hex only), `water_volume_fraction` and `lipid_volume_fraction`.

## Inputs and units

| Input | Unit | Description |
|---|---|---|
| `phase` | – | `Pn3m`, `Im3m`, `Ia3d`, `Hex` or `La` |
| `lattice` | nm | lattice parameter *a*, from SAXS |
| `water` | % weight | water used to prepare the mesophase |
| `density` | g/cm³ | density of the lipid (water is taken as 1 g/cm³) |

## Model

The water volume fraction φ<sub>w</sub> follows from the water weight percentage *c*<sub>w</sub> and the lipid density ρ<sub>L</sub>:

$$\phi_w = 1 - \frac{1}{1 + \rho_L\, c_w/(100 - c_w)}, \qquad \phi_L = 1 - \phi_w .$$

**Bicontinuous cubic phases.** The lipid length *L* is the solution of
(Turner et al.)

$$\phi_L = 2A_0\,\frac{L}{a} + \frac{4\pi}{3}\,\chi \left(\frac{L}{a}\right)^3 ,$$

and the radius of the water channels is (Briggs et al.)

$$r = a\sqrt{-\frac{A_0}{2\pi\chi}} - L ,$$

where *A*<sub>0</sub> and χ are the unit-cell area and Euler–Poincaré characteristic of the underlying minimal surface:

| Phase | *A*<sub>0</sub> | χ |
|---|---|---|
| Pn3m | 1.919 | −2 |
| Im3m | 2.345 | −4 |
| Ia3d | 3.091 | −8 |

**Inverse hexagonal phase** (Seddon): r = a √(√3 φ<sub>w</sub> / 2π). Two lipid lengths are given: the unfrustrated length L<sub>unf</sub> = a/2 − r (Seddon; Mezzenga et al.) and the average length L<sub>ave</sub> = (3 ln 3 / 2π) a − r.

**Lamellar phase:** water lamellae of thickness d<sub>w</sub> = a φ<sub>w</sub> and lipid length L = a φ<sub>L</sub>/2.

## Tests

```bash
python -m unittest discover tests
```

The tests check that the results match the online tool.

## How to cite

If you use this tool in your research, please cite:

- S. Assenza and R. Mezzenga, *J. Chem. Phys.* **148**, 054902 (2018). [doi:10.1063/1.5019224](https://doi.org/10.1063/1.5019224)

and the original derivations:

- D. C. Turner, Z.-G. Wang, S. M. Gruner, D. A. Mannock and R. N. McElhaney, *J. Phys. II France* **2**, 2039 (1992)
- J. Briggs, H. Chung and M. Caffrey, *J. Phys. II France* **6**, 723 (1996)
- J. M. Seddon, *Biochim. Biophys. Acta* **1031**, 1 (1990)
- R. Mezzenga et al., *Langmuir* **21**, 3322 (2005)

See also the companion tool [MesophaseDiffusion](https://github.com/saassenza/MesophaseDiffusion), which estimates diffusion coefficients in cubic phases.

## License

MIT, see [LICENSE](LICENSE).

## Contact

Salvatore Assenza, Universidad Autónoma de Madrid (IFIMAC)
