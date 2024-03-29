import operator
from collections import defaultdict
from collections.abc import Iterable
from ..constants import *
from . import rtypes
from ..utils import util

in_type_casts = defaultdict(list)
cast_exec = defaultdict(dict)

class CheckEnv(object):
    """Object holding attributes to check cast"""
    __slots__ = ['out_type_cls', 'checktypesfunc', 'simtypefunc', 'name']
    def __init__(self, out_type_cls, checktypesfunc, simtypefunc, name):
        self.out_type_cls = out_type_cls
        self.checktypesfunc = checktypesfunc
        self.simtypefunc = simtypefunc
        self.name = name

def addCasts(in_type_cls, out_type_cls, checktypesfunc, simtypefunc, castname):
    """Add cast
        in_type_cls: in type class, can also be sequence
        out_type_cls: out type class, can also be sequence
        checktypefunc: function to check actual types for compatibility
        simtypefunc: function to create best matching out_type if possible
    """
    if(isinstance(out_type_cls, Iterable)):
        if(not isinstance(out_type_cls, set)):
            out_type_cls = set(out_type_cls)
    else:
        out_type_cls = set([out_type_cls])
    
    checkenv = CheckEnv(out_type_cls, checktypesfunc, simtypefunc, castname) 
    
    if(isinstance(in_type_cls, Iterable)):
        for incls in in_type_cls:
            in_type_casts[incls].append(checkenv)
    else:
        in_type_casts[in_type_cls].append(checkenv)

def findImplicitCastTypes(in_type_cls):
    """Returns type classes that can be casted to without loss of information"""
    res = set(in_type_cls.__mro__[1:])
    res.add(in_type_cls)
    return res 

def canCast(intype, outtype, dimdepth):
    if(not intype.__class__ in in_type_casts):
        return False
    
    pos_casts = in_type_casts[intype.__class__]

    if(isinstance(outtype, rtypes.TypeUnknown)):
        for pos_cast in pos_casts:
            if(outtype.__class__ in pos_cast.out_type_cls and
               pos_cast.checktypesfunc(intype, outtype)):
                return pos_cast.name
    else:
        for pos_cast in pos_casts:        
            if(outtype in pos_cast.out_type_cls):
                otype = pos_cast.simtypefunc(intype, outtype, dimdepth)
                return (otype, pos_cast.name)
    return False

def castImplicitCommonType(*types):
    types = list(types)
    while len(types) > 1:
        t1 = types.pop()
        types[-1] = castImplicitCommonTypeDual(t1,types[-1])
    return types[-1]

def castImplicitCommonTypeDual(type1, type2):
    if(type1 == type2):
        return type1

    in1_impli_cls = findImplicitCastTypes(type1.__class__)
    in2_impli_cls = findImplicitCastTypes(type2.__class__)
    out_impli_cls = in1_impli_cls & in2_impli_cls

    while out_impli_cls:
        out_cls = rtypes.mostSpecializedTypesCls(out_impli_cls)
        assert len(out_cls) == 1, \
            "Multiple implicit common types found"
        out_cls = out_cls[0]
        res = out_cls.commonType(type1, type2)
        if(not res is False):
            break
        out_impli_cls.discard(out_cls)
    return res

def castMultipleImplicitCommonType(*types):
    assert types, "No types given to cast function"
    types = list(types)
    while(len(types) > 1):
        types.append(castImplicitCommonType(types.pop(),types.pop()))
    return types[0]

############
# CAST: check type functions
############
def checkDefault(intype, outtype):#{{{
    return True

def simDefault(intype, outtypecls, dimdepth):
    return outtypecls(intype.has_missing)

def simSame(intype, outtypecls, dimdepth):
    return outtypecls(intype.has_missing, dims=intype.dims)


#}}}
addCasts(rtypes.TypeNumbers | set([rtypes.TypeAny, rtypes.TypeUnknown]), rtypes.TypeNumbers, checkDefault, simDefault,"to_numbers")
addCasts(rtypes.TypeAll, set([rtypes.TypeAny, rtypes.TypeUnknown]), checkDefault, simDefault,"to_any")
addCasts(set([rtypes.TypeUnknown, rtypes.TypeAny]) | rtypes.TypeStrings, rtypes.TypeIntegers, checkDefault, simDefault,"string_to_int")
addCasts(set([rtypes.TypeUnknown, rtypes.TypeAny]) | rtypes.TypeStrings, rtypes.TypeReals, checkDefault, simDefault,"string_to_real")
addCasts(set([rtypes.TypeUnknown, rtypes.TypeAny]) | rtypes.TypeStrings, rtypes.TypeStrings, checkDefault, simDefault,"string_to_string")






def checkStringString(intype, outtype):
    if(intype.has_missing and not outtype.has_missing):
        return False

    if intype.dims[0].shape == UNDEFINED and not outtype.dims[0].shape == UNDEFINED:
        return False
    elif intype.dims[0].shape != UNDEFINED and intype.dims[0].shape > outtype.dims[0].shape:
        return False
    return True

def simStringString(intype, outtypecls, dimdepth):
    return intype

addCasts([rtypes.TypeBytes,rtypes.TypePickle], [rtypes.TypeBytes,rtypes.TypePickle], checkStringString, simStringString,"string_to_string")#}}}

def checkPickle(intype, outtype):
    if(intype.has_missing and not outtype.has_missing):
        return False

    if not outtype.dims[0].shape == UNDEFINED:
        return False
    return True

def simPickle(intype, outtypecls, dimdepth):
    ndim = dimensions.Dim(UNDEFINED, (True,) * dimdepth, intype.has_missing)
    return rtypes.TypePickle(dims=dimpaths.DimPath(ndim))

addCasts(rtypes.TypeAll, rtypes.TypePickle, checkPickle, simPickle,"to_pickle")

def simDePickle(intype, outtypecls, dimdepth):
    return rtypes.unknown

addCasts(rtypes.TypePickle, rtypes.TypeAll, checkDefault, simDePickle,"from_pickle")


def checkStringSetToArray(intype, outtype):
    if(intype.has_missing and not outtype.has_missing):
        return False
    
    if len(outtype.dims) != 1:
        return False

    if not intype.dims[0].shape == outtype.dims[0].shape or not intype.dims[0].dependent == outtype.dims[0].dependent:
        return False

    if not intype.subtypes == outtype.subtypes:
        return False
    return True

def simStringSetToArray(intype, outtypecls, dimdepth):
    return rtypes.TypeArray(has_missing=intype.has_missing, dims=intype.dims, subtypes=intype.subtypes)

addCasts(rtypes.TypeStrings | set([rtypes.TypeSet]), rtypes.TypeArray, checkStringSetToArray, simStringSetToArray,"to_array")
    

def checkBytes(intype, outtype):
    if(not isinstance(outtype,rtypes.TypeBytes)):
        return False
    return True

def simBytes(intype, outtypecls, dimdepth):
    ndim = dimensions.Dim(UNDEFINED, (True,) * dimdepth, intype.has_missing)
    return types.TypeBytes(dims=dimpaths.DimPath(ndim),has_missing=intype.has_missing)

addCasts(rtypes.TypeAll, rtypes.TypeBytes, checkBytes, simBytes,"to_bytes")

def checkString(intype, outtype):
    if(not isinstance(outtype,rtypes.TypeString)):
        return False
    return True

def simString(intype, outtypecls, dimdepth):
    ndim = dimensions.Dim(UNDEFINED, (True,) * dimdepth, intype.has_missing)
    return types.TypeString(dims=dimpaths.DimPath(ndim),has_missing=intype.has_missing)

addCasts(rtypes.TypeAll, rtypes.TypeString, checkString, simString,"to_string")



def checkArrayToArray(intype, outtype):
    if(intype.has_missing and not outtype.has_missing):
        return False
   
    if len(intype.dims) != len(outtype.dims):
        return False

    for d1,d2 in zip(intype.dims, outtype.dims):
        if d1.shape == d2.shape:
            if d1.shape == UNDEFINED:
                #TODO: cast undefined fixed shape to undefined fixed shape
                #we would have to check if they are the same during runtime
                return False
            if d1.dependent != d2.dependent:
                return False

    if not checkSubType(intype.subtypes[0], outtype.subtypes[0]):
        return False
    return True
   
def simArrayToArray(intype, outtypecls, dimdepth):
    return outtypecls(has_missing=intype.has_missing, dims=intype.dims, subtypes=intype.subtypes)


addCasts(set([rtypes.TypeArray]), set([rtypes.TypeArray]), checkArrayToArray, simArrayToArray,"copy")

def checkTupleToTuple(intype, outtype):
    if(intype.has_missing and not outtype.has_missing):
        return False
    
    for s1,s2 in zip(intype.subtypes, outtype.subtypes):
        if not checkSubType(s1,s2):
            return False

    return True

def simTupleToTuple(intype, outtypecls, dimdepth):
    return outtypecls(has_missing=intype.has_missing, dims=intype.dims, subtypes=intype.subtypes)

addCasts(set([rtypes.TypeTuple]), set([rtypes.TypeTuple]), checkTupleToTuple, simTupleToTuple,"copy")

def checkSubType(intype, outtype):
    if isinstance(intype, tuple(rtypes.TypeStrings)):
        if not checkStringString(intype, outtype):
            return False
    elif isinstance(intype,rtypes.TypeArray):
        if not checkArrayToArray(intype,outtype):
            return False
    elif isinstance(intype, rtypes.TypeTuple):
        if not checkTupleToTuple(intype, outtype):
            return False
    else:
        if not intype <= outtype:
            return False
    return True
   




