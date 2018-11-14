from units.datatypes import UnitVal,Unit
from units.unit      import K,Pa,m,J
################################################################################
class SafeConstructor(UnitVal):
    '''
    Superclass for Safe Constructors, which can be wrapped around any value
        to assert to the typechecker that this value is of a certain unit.

     The only content of this superclass is to provide a means of enforcing
        a runtime assertion that our promise was upheld... so that one cannot,
        for example, do something like:
            >>> totally_a_length = Length(100 * years)

    '''
    def __init__(self,default:Unit, val_:UnitVal)->None:

        # Handle receiving a UnitVal vs just a float differently
        #-------------------------------------------------------
        val, unit = val_.val, val_.unit
        assert unit.bases == default.bases,  'invalid unit: %s'%unit #

        # Do normal UnitVal stuff
        super().__init__(val,unit)

############
# Examples #
############

class Temp(SafeConstructor):
    """ Assures typechecker that this value is a temperature """
    def __init__(self, val_ : UnitVal) -> None:
        super().__init__(K, val_)

class Pressure(SafeConstructor):
    """ Assures typechecker that this value is a temperature """
    def __init__(self, val_ : UnitVal) -> None:
        super().__init__(Pa, val_) 

class Length(SafeConstructor):
    """ Assures typechecker that this value is a length """
    def __init__(self, val_ : UnitVal) -> None:
        super().__init__(m, val_) # <--- default unit is first argument

class Energy(SafeConstructor):
    """ Assures typechecker that this value is an energy """
    def __init__(self, val_ : UnitVal) -> None:
        super().__init__(J, val_) # <--- default unit is first argument
