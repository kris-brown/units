from typing import Dict,Union as U, Optional as O, Callable as C
from enum  import Enum

Num   = U[float,int]
################################################################################

class Unit(object):
    """SI-derived units expressible as constant multiplicative
        and (then) additive factors for some product of base units
    """
    def __init__(self,
                 label   : str                  = '',
                 bases   : Dict['SIBase',float] = {},
                 factor  : float                = 1,
                 offset  : float                = 0
                ) -> None:
        self._label  = label
        self._factor = factor
        self._offset = offset
        self._bases  = bases

    def __eq__(self,other:object)->bool:
        """
        Important: labels don't matter for equality
        """
        err = 'Cannot compare Units to %s for equality'%(type(other))
        assert isinstance(other,Unit), err
        return (    self.factor == other.factor
                and self.offset == other.offset
                and self.bases  == other.bases)

    def __str__(self)->str:
        '''
        Laborious method for representing a unit
        '''
        basedict  = {pow:k.value for k,pow in self.bases.items() if pow !=0}
        strbases  = dict([(y,x) for x,y in reversed(sorted(basedict.items()))])
        strfactor = ' x %s'%self.factor if self.factor!=1 else ''
        plus      = '+' if self.offset > 0 else ''
        stroffset = ' %s %s'%(plus,self.offset) if self.offset!=0 else ''
        fmtargs   = [self.label,strbases,strfactor,stroffset]
        return '{} ({}{}{})'.format(*fmtargs)

    __repr__ = __str__

    @property
    def factor(self) -> float:
        return self._factor

    @property
    def label(self) -> str:
        return self._label

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
        n = self.label+'·'+u.label
        basesum = {b:self.bases[b]+u.bases[b] for b in SIBase}
        return Unit(n,basesum,self.factor*u.factor)

    def __truediv__(self,u : 'Unit')->'Unit':
        err = 'Cannot divide a derived unit with an offset (meter*Celsius is ridiculous)'
        assert self.offset == 0, err
        n = self.label+'·'+u.label
        basediff = {b:self.bases[b] - u.bases[b] for b in SIBase}
        return Unit(n,basediff,self.factor*u.factor)

    def __rtruediv__(self,v : float)->'UnitVal':
        '''E.g. 2 / m ==> 2.0 m^(-1)'''
        return UnitVal(v) / self

    def __rfloordiv__(self,v : int)->'Unit':
        '''E.g. 1 / s ==> Hz '''
        assert v == 1,          ' // operator requires numerator to be 1'
        assert self.offset == 0, 'Cannot invert derived unit with offset (e.g. 1/C)'
        return Unit('1/'+self.label,{b:-v for b,v in self.bases.items()},1/self.factor)

    def __pow__(self, pow : Num) -> 'Unit':
        err = 'Cannot exponeniate a derived unit with an offset (Celsius^2 is ridiculous)'
        assert self.offset == 0, err
        n = self.label+'^%s'%pow
        return Unit(n,{b:p*pow for b,p in self.bases.items()},self.factor**pow)

    def toUnit(self,label:str) -> 'Unit':
        """
        Create a unit out of a UnitVal.
        yard = (1.05 * m).unit() means there are 1.05 meters in a yard
        """
        assert self.factor == 1 and self.offset == 0
        return Unit(label,self.bases)

    def stdLabel(self)->'Unit':
        basedict  = {pow:k.value for k,pow in self.bases.items() if pow !=0}
        strbases  = reversed(sorted(basedict.items()))
        n = '·'.join([b+('^%s'%(pow) if pow!=1 else '') for pow,b in strbases])
        return Unit(n,self.bases,self.factor,self.offset)

class SIBase(Unit,Enum):
    """Base SI unit types"""
    KILOGRAM = 'kg'
    SECOND   = 's'
    KELVIN   = 'K'
    AMPERE   = 'A'
    MOLE     = 'mol'
    METER    = 'm'

    def unit(self)->Unit:
        return Unit(label=self.label,bases=self.bases)

    def __pow__(self, pow : Num) -> Unit:
        return  self.unit() ** pow
    def __str__(self)->str:
        return self.value

    # Skeletons in the basement
    __init__ = Enum.__init__ # type: ignore
    __eq__   = Enum.__eq__
    __hash__ = Enum.__hash__

    @property
    def factor(self)->float: return 1

    @property
    def offset(self)->float: return 0

    @property
    def label(self)->str: return self.value # type: ignore

    @property
    def bases(self)->Dict['SIBase',float]:
        return {b:(1 if b == self else 0) for b in SIBase}

class UnitVal(object):
    """
    A value accompanied by a unit
    Most places where we typically use floats should be replaced with this
    """
    def __init__(self,val:float=1.0,unit:O[Unit] = None)->None:
        unit_ = unit or Unit()
        self.val=val; self.unit= unit_

    def __call__(self)->float:
        """Return value in SI units"""
        return (self.val - self.unit.offset)/self.unit.factor

    def __str__(self)->str:
        return '%s %s'%(self.val,self.unit)

    __repr__ = __str__

    def __add__(self, u : 'UnitVal') -> 'UnitVal':
        """Product of two values with units"""
        assert self.unit == u.unit, 'Cannot add numbers of different units'
        return UnitVal(val = self.val + u.val, unit = self.unit*u.unit)

    def __sub__(self, u : 'UnitVal') -> 'UnitVal':
        """Product of two values with units"""
        assert self.unit == u.unit, 'Cannot subtract numbers of different units'
        return UnitVal(val = self.val - u.val, unit = self.unit*u.unit)

    def __mul__(self, u : U['UnitVal',Unit]) -> 'UnitVal':
        """Product of two values with units"""
        val,unit = (u.val,u.unit) if isinstance(u,UnitVal) else (1,u)
        return UnitVal(val = self.val * val,unit = self.unit*unit)

    def __truediv__(self, u : U['UnitVal',Unit]) -> 'UnitVal':
        val,unit = (u.val,u.unit) if isinstance(u,UnitVal) else (1,u)
        return UnitVal(val = self.val / val, unit = self.unit/unit)

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

    def toUnit(self,label:str) -> Unit:
        """
        Create a unit out of a UnitVal.
        yard = (1.05 * m).unit() means there are 1.05 meters in a yard
        """
        return Unit(label=label,bases=self.unit.bases,factor=self.unit.factor * self.val)

    def to(self,u_:O[Unit]=None)->'UnitVal':
        """
        Convert from one unit to another of the same type.
        If none specified, then converts to SI units
        """
        err = 'Cannot convert %s to %s'
        u = u_ or Unit(bases = self.unit.bases)
        assert u.bases == self.unit.bases, err%(self.unit,u)
        self_si = (self.val-self.unit.offset)/self.unit.factor
        return UnitVal(val = (self_si*u.factor)+u.offset, unit = u)

    def stdLabel(self)->'UnitVal':
        '''Convert the unit into standard name'''
        return UnitVal(val = self.val, unit = self.unit.stdLabel())
