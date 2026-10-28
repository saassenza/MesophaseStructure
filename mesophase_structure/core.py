"""Structural parameters of lipid mesophases from SAXS lattice parameters.

Python port of the "Structural info of mesophases" tool available at
https://www.salvatoreassenza.com/#tools. Results are identical to the online tool.

Supported phases
----------------
- Bicontinuous cubic phases Pn3m, Im3m and Ia3d: lipid length following
  Turner et al., J. Phys. II 2, 2039 (1992); water-channel radius following
  Briggs et al., J. Phys. II 6, 723 (1996).
- Inverse hexagonal phase (Hex): channel radius following Seddon,
  Biochim. Biophys. Acta 1031, 1 (1990). Two lipid lengths are returned: the
  unfrustrated length L_unf (Seddon; Mezzenga et al., Langmuir 21, 3322 (2005))
  and the average length L_ave.
- Lamellar phase (La): lipid length and thickness of the water lamellae.

Units: lengths in nm, densities in g/cm^3, water content in % weight.
The density of water is taken as 1 g/cm^3.
"""

import math
from dataclasses import dataclass
from typing import Optional

#: Minimal-surface parameters (A0: surface area of the unit cell in units of
#: a^2; chi: Euler-Poincare characteristic) of the bicontinuous cubic phases.
CUBIC_GEOMETRY = {
    "Pn3m": (1.919, -2),
    "Im3m": (2.345, -4),
    "Ia3d": (3.091, -8),
}

PHASES = ("Pn3m", "Im3m", "Ia3d", "Hex", "La")


@dataclass
class StructureResult:
    """Structural parameters of a mesophase (lengths in nm).

    radius:                water-channel radius (cubic and Hex phases)
    water_thickness:       thickness of the water lamellae (La phase)
    lipid_length:          lipid length (for Hex: unfrustrated length L_unf)
    lipid_length_average:  average lipid length L_ave (Hex phase only)
    """

    phase: str
    lattice: float
    water_volume_fraction: float
    lipid_volume_fraction: float
    lipid_length: float
    radius: Optional[float] = None
    water_thickness: Optional[float] = None
    lipid_length_average: Optional[float] = None


def _check_phase(phase):
    if phase not in PHASES:
        raise ValueError("Unknown phase %r; choose among %s" % (phase, ", ".join(PHASES)))


def water_volume_fraction(water_weight, lipid_density):
    """Volume fraction of water from its weight percentage and the lipid density."""
    if not 0 < water_weight < 100:
        raise ValueError("Water content must be between 0 and 100 % weight")
    if lipid_density <= 0:
        raise ValueError("Lipid density must be positive")
    return 1 - 1 / (1 + lipid_density * water_weight / (100 - water_weight))


def cubic_lipid_length(lattice, phase, lipid_volume_fraction):
    """Lipid length (nm) in a bicontinuous cubic phase.

    Solves phi_lipid = 2 A0 x + (4/3) pi chi x^3 for x = L/a (Turner et al.).
    """
    if phase not in CUBIC_GEOMETRY:
        raise ValueError("Phase %r is not a bicontinuous cubic phase" % phase)
    a0, chi = CUBIC_GEOMETRY[phase]
    p = 3 * a0 / (2 * math.pi * chi)
    q = -3 * lipid_volume_fraction / (4 * math.pi * chi)
    arg = 3 * q / (2 * p) * math.sqrt(-3 / p)
    if not -1 <= arg <= 1:
        raise ValueError("No physical solution: lipid volume fraction %.3f too large for %s"
                         % (lipid_volume_fraction, phase))
    x = 2 * math.sqrt(-p / 3) * math.cos(math.acos(arg) / 3 - 2 * math.pi / 3)
    return x * lattice


def cubic_channel_radius(lattice, phase, lipid_length):
    """Water-channel radius (nm) in a bicontinuous cubic phase (Briggs et al.)."""
    a0, chi = CUBIC_GEOMETRY[phase]
    return math.sqrt(-a0 / (2 * math.pi * chi)) * lattice - lipid_length


def structure(phase, lattice, water_weight, lipid_density):
    """Compute the structural parameters of a lipid mesophase.

    Parameters
    ----------
    phase : str
        One of "Pn3m", "Im3m", "Ia3d", "Hex", "La".
    lattice : float
        Lattice parameter in nm, as measured by SAXS.
    water_weight : float
        Weight percentage of water used to prepare the mesophase.
    lipid_density : float
        Density of the lipid in g/cm^3.
    """
    _check_phase(phase)
    if lattice <= 0:
        raise ValueError("Lattice parameter must be positive")
    phi_w = water_volume_fraction(water_weight, lipid_density)
    phi_l = 1 - phi_w
    res = StructureResult(phase=phase, lattice=lattice, water_volume_fraction=phi_w,
                          lipid_volume_fraction=phi_l, lipid_length=float("nan"))

    if phase == "Hex":
        r = lattice * math.sqrt(0.5 * math.sqrt(3) / math.pi * (1 - phi_l))
        res.radius = r
        res.lipid_length = 0.5 * lattice - r
        res.lipid_length_average = 1.5 * math.log(3) / math.pi * lattice - r
    elif phase == "La":
        res.water_thickness = lattice * (1 - phi_l)
        res.lipid_length = 0.5 * lattice * phi_l
    else:
        length = cubic_lipid_length(lattice, phase, phi_l)
        res.lipid_length = length
        res.radius = cubic_channel_radius(lattice, phase, length)
    return res
