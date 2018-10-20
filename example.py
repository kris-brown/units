from units.unit         import m,s,J,kg,K
from units.datatypes    import UnitVal
from units.constructor  import Temp,Energy
###############################################################################
def test()->None:
    ######################
    # Example arithmatic #
    ######################

    len1    = 100 * m
    len2    = 10 * m
    time1   = 1 * s
    ratio1  = len1 / len2
    veloc1  = len1 / time1

    float(ratio1) # no problem
    try:
        float(veloc1) # runtime error: it's not unitless!
    except Exception as e:
        print(e)

    eng1   = 5 * J
    eng2   = 3 * kg * m**2 / s**2
    eng3   = eng1 + eng2 # no problem
    try:
        eng4 = eng1 + len1 # runtime error: not the same units
    except Exception as e:
        print(e)

    ###############################
    # "Safe constructor" examples #
    ###############################
    def doThermo1(t:UnitVal)->UnitVal:
        '''
        It's a function and we really know it's only valid if arg is a temperature
        The minimum due diligence is to have the typechecker assert inputs and
        outputs are UnitVals
        '''
        boltzmann = 1.38e-23 * J / K
        return t * boltzmann

    def doThermo2(t:Temp)->UnitVal:
        '''
        However, we can enforce that the input argument is a temperature
        '''
        boltzmann = 1.38e-23 * J / K
        return t * boltzmann

    def doThermo3(t:Temp)->Energy:
        '''and also make a guarantee about the output unit type'''
        boltzmann = 1.38e-23 * J / K
        return Energy(t * boltzmann)


    temp1 = Temp(100 * K)

    doThermo1(len1)       # no TYPE ERROR, because we were LAZY
    doThermo2(len1)       # type: ignore # <------ type error

    try:
        Temp(len1) # cannot wrap a non-temperature in Temp()
    except Exception as e:
        print(e)

    doThermo2(temp1)      # typechecks, no runtime error

    def energyThing(e:Energy)->None:
        print('The ENERGY is ',e)

    energyThing(doThermo2(temp1)) # type: ignore # <----- type error
    energyThing(doThermo3(temp1)) # no type error
    import pdb;pdb.set_trace()

if __name__=='__main__':
    test()
