
"""
@file    openxc-python\openxc\units.py OpenXC Units Script
@author  Christopher Peplin github@rhubarbtech.com
@date    June 25, 2013
@version 0.9.4

@brief   Define the scalar units used by vehicle measurements."""

from __future__ import absolute_import

import sys
from units import unit, scaled_unit, named_unit
import units.predefined

units.predefined.define_units()

## @var Percentage
# The percentage unit.
Percentage = unit('%')
## @var Meter
# The meter unit.
Meter = unit('m')
## @var Kilometer
# The Kilometer unit.
Kilometer = scaled_unit('m', 'km', 1000)
## @var Hour
# The Hour unit.
Hour = unit('h')
## @var KilometersPerHour
# The KilometersPerHour unit.
KilometersPerHour = unit('km') / unit('h')
## @var RotationsPerMinute
# The RotationsPerMinute unit.
RotationsPerMinute = unit('rotations') / unit('m')
## @var Litre
# The Litre unit.
Litre = unit('L')
## @var Degree
# The Degree unit.
Degree = unit('deg')
## @var NewtonMeter
# The NewtonMeter unit.
NewtonMeter = named_unit("Nm", ["N", "m"], [])
## @var MetersPerSecondSquared
# The MetersPerSecondSquared unit.
MetersPerSecondSquared = unit('m') / (pow(unit('s'), 2))
## @var Undefined
# The Undefined unit.
Undefined = unit('undef')
