"""Define the scalar units used by vehicle measurements."""
from __future__ import absolute_import

import sys
from units import unit, scaled_unit, named_unit
import units.predefined

units.predefined.define_units()


Percentage = unit('%')
Meter = unit('m')
Kilometer = scaled_unit('m', 'km', 1000)
Hour = unit('h')
KilometersPerHour = unit('km') / unit('h')
RotationsPerMinute = unit('rotations') / unit('m')
Litre = unit('L')
Degree = unit('deg')
NewtonMeter = named_unit("Nm", ["N", "m"], [])
MetersPerSecondSquared = unit('m') / (pow(unit('s'), 2))
Undefined = unit('undef')
