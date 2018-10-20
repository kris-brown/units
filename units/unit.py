from units.datatypes import SIBase,Unit

################################################################################
# EXAMPLE UNITS #
#################

# SI base units
#--------------
kg  = SIBase['KILOGRAM']# type: SIBase
s   = SIBase['SECOND']  # type: SIBase
K   = SIBase['KELVIN']  # type: SIBase
A   = SIBase['AMPERE']  # type: SIBase
mol = SIBase['MOLE']    # type: SIBase
m   = SIBase['METER']   # type: SIBase


# SI-Derived units
#-----------------
C   = Unit('C',{K:1}, offset = -273.15)
F   = Unit('F',{K:1}, factor = 9/5, offset = -459.67)
N   = kg * (m/s**2)
J   = N * m
Pa  = (N / m**2).toUnit('Pa')
bar = (1e5 *Pa).toUnit('bar')
eV  = (1/6.242e+18 * J).toUnit('eV')
Hz  = 1 // s
