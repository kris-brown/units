from typing import Any,Dict,Union as U, Optional as O
from enum  import Enum

Num   = U[float,int]
################################################################################

class Unit(object):
    """SI-derived units expressible as constant multiplicative
        and (then) additive factors for some product of base units

    E.g. Farenheit is NOT an SI-derived unit (requires adding, multiplying,
        then adding again), but Celsius is.
    """
    def __init__(self,
                 bases  : Dict['SIBase',float],
                 factor : float = 1,
                 offset : float = 0
                ) -> None:
        self._factor = factor
        self._offset = offset
        self._bases  = bases

    def __eq__(self,other:object)->bool:
        err = 'Cannot compare Units to %s for equality'%(type(other))
        assert isinstance(other,Unit), err
        return (self.factor     == other.factor
                and self.offset == other.offset
                and self.bases  == other.bases)

    def __str__(self)->str:
        '''Laborious method for representing a unit'''
        basedict  = {pow:k.value for k,pow in self.bases.items() if pow !=0}
        strbases  = str(dict([(y,x) for x,y in sorted(basedict.items())]))
        strfactor = 'x %s'%self.factor if self.factor!=1 else ''
        plus      = '+' if self.offset > 0 else ''
        stroffset = '%s %s'%(plus,self.offset) if self.offset!=0 else ''
        fmtargs   = [strbases,strfactor,stroffset]
        return '{} {} {}'.format(*fmtargs)

    __repr__ = __str__

    @property
    def factor(self) -> float:
        return self._factor

    @property
    def offset(self) -> float:
        return self._offset

    @property
    def bases(self) -> Dict['SIBase',float]:
        return {b:self._bases.get(b,0) for b in SIBase}

    def __rmul__(self, val : Num) -> 'UnitVal':
        return UnitVal(val,self)

    def __mul__(self,u : 'Unit')->'Unit':
        err = 'Cannot multiply a derived unit with an offset (meter*Celsius is ridiculous)'
        assert self.offset == 0, err
        return Unit({b:self.bases[b]+u.bases[b] for b in SIBase},self.factor*u.factor)

    def __truediv__(self,u : 'Unit')->'Unit':
        err = 'Cannot divide a derived unit with an offset (meter*Celsius is ridiculous)'
        assert self.offset == 0, err
        return Unit({b:self.bases[b]-u.bases[b] for b in SIBase},self.factor*u.factor)

    def __pow__(self, pow : Num) -> 'Unit':
        err = 'Cannot exponeniate a derived unit with an offset (Celsius^2 is ridiculous)'
        assert self.offset == 0, err
        return Unit({b:p*pow for b,p in self.bases.items()},self.factor**pow)

class SIBase(Unit,Enum):
    """Base SI unit types"""
    KILOGRAM = 'kg'
    SECOND   = 's'
    KELVIN   = 'K'
    AMPERE   = 'A'
    MOLE     = 'mol'
    METER    = 'm'

    def unit(self)->Unit:
        return Unit(self.bases)

    def __pow__(self, pow : Num) -> Unit:
        return  self.unit() ** pow

    __eq__   = Enum.__eq__
    __hash__ = Enum.__hash__

    @property
    def factor(self)->float: return 1

    @property
    def offset(self)->float: return 0

    @property
    def bases(self)->Dict['SIBase',float]:
        return {b:(1 if b == self else 0) for b in SIBase}

class UnitVal(object):
    """
    A value accompanied by a unit
    Most places where we typically use floats should be replaced with this
    """
    def __init__(self,val:float,unit:Unit)->None:
        self.val=val; self.unit= unit

    def __call__(self)->float:
        """Return value in SI units"""
        return (self.val - self.unit.offset)/self.unit.factor

    def __str__(self)->str:
        return '%s %s'%(self.val,self.unit)

    __repr__ = __str__

    def __add__(self, u : 'UnitVal') -> 'UnitVal':
        """Product of two values with units"""
        assert self.unit == u.unit, 'Cannot add numbers of different units'
        return UnitVal(self.val + u.val,self.unit*u.unit)

    def __sub__(self, u : 'UnitVal') -> 'UnitVal':
        """Product of two values with units"""
        assert self.unit == u.unit, 'Cannot subtract numbers of different units'
        return UnitVal(self.val - u.val,self.unit*u.unit)

    def __mul__(self, u : U['UnitVal',Unit]) -> 'UnitVal':
        """Product of two values with units"""
        val,unit = (u.val,u.unit) if isinstance(u,UnitVal) else (1,u)
        return UnitVal(self.val * val,self.unit*unit)

    def __truediv__(self, u : U['UnitVal',Unit]) -> 'UnitVal':
        val,unit = (u.val,u.unit) if isinstance(u,UnitVal) else (1,u)
        return UnitVal(self.val / val,self.unit/unit)

    def __float__(self)->float:
        """Cast unitval into a unitless floating number - throws error if has units"""
        uerr = 'Cannot cast into unitless number: %s'%self.unit
        assert all([x == 0 for x in self.unit.bases.values()]), uerr
        return self.val

    def __int__(self)->int:
        """Cast unitval into an integer - throws error if has units"""
        uerr = 'Cannot cast into unitless number: %s'%self.unit
        assert all([x == 0 for x in self.unit.bases.values()]), uerr
        assert int(self.val) == self.val, 'Cannot cast to integer! %s'%self.val
        return int(self.val)

    def toUnit(self)->Unit:
        """
        Create a unit out of a UnitVal.
        yard = (1.05 * m).unit() means there are 1.05 meters in a yard
        """
        return Unit(self.unit.bases,self.unit.factor * self.val)

class SafeConstructor(UnitVal):
    '''
    Superclass for Safe Constructors, which can be wrapped around any value
        to assert to the typechecker that this value is of a certain unit.
     The only content of this superclass is to provide a means of enforcing
        a runtime assertion that our promise was upheld so that one cannot, for
        example, do something like:
            >>> totally_a_length = Length(100 * years)

    The constructors are designed so that they can either take just a float
    (which is cast to the UnitVal with the correct units) or a UnitVal (whose
    unit gets checked at runtime)
     '''
    def __init__(self,default:Unit, val_:UnitVal)->None:

        # Handle receiving a UnitVal vs just a float differently
        #-------------------------------------------------------
        val,unit = val_.val,val_.unit
        assert unit.bases == default.bases,  'invalid unit: %s'%unit #

        # Do normal UnitVal stuff
        super().__init__(val,unit)

class Temp(SafeConstructor):
    """ Assures typechecker that this value is a temperature """
    def __init__(self, val_ : UnitVal) -> None:
        super().__init__(K, val_) # <--- default unit is first argument

class Length(SafeConstructor):
    """ Assures typechecker that this value is a length """
    def __init__(self, val_ : UnitVal) -> None:
        super().__init__(m, val_) # <--- default unit is first argument

class Energy(SafeConstructor):
    """ Assures typechecker that this value is an energy """
    def __init__(self, val_ : UnitVal) -> None:
        super().__init__(J, val_) # <--- default unit is first argument

#################
# EXAMPLE UNITS #
#################

# SI units
#----------
kg  = SIBase['KILOGRAM']
s   = SIBase['SECOND']
K   = SIBase['KELVIN']
A   = SIBase['AMPERE']
mol = SIBase['MOLE']
m   = SIBase['METER']

# SI-Derived units
#-----------------
C  = Unit({K:1}, offset = -273.15)
N  = kg * (m/s**2)
J  = N * m
eV = (1/6.242e+18 * J).toUnit()
