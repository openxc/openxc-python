from __future__ import absolute_import

import sys
from units import unit, scaled_unit, named_unit
import units.predefined


def monkey_patch_units():
    """The units library doesn't support Python3 out of the box, but it's really
    close. This function monkey patches a few things that make it compatible,
    and it can be phased out when the units library is updated.
    """
    from units.leaf_unit import LeafUnit
    from units.named_composed_unit import NamedComposedUnit
    # Division changed in Python 3 so there are now two methods that can be
    # overridden, __truediv__ for the "/" operator and __floordiv__ for "//".
    LeafUnit.__truediv__ = LeafUnit.__div__
    NamedComposedUnit.__truediv__ = NamedComposedUnit.__div__

    # Previously, objects without a __cmp__ method could be implicitly compared
    # by their ids. It gave a consistent order for 1 program runtime. The __lt__
    # method is now required for sorting, and here we just use the identity
    # which should have the same effect.
    def less_than_by_id(self, other):
        return id(self) < id(other)
    LeafUnit.__lt__ = less_than_by_id


    # Again, no more __cmp__
    from units.quantity import Quantity
    Quantity.__lt__ = Quantity.__cmp__


    # No more cmp function either, so these must be redefined
    def cmp(a, b):
        return (a > b) - (a < b)

    import units.quantity
    units.quantity.cmp = cmp

if sys.version_info[:2] >= (3, 0):
    monkey_patch_units()

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

