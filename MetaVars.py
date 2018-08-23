import os.path
import sys
import SimpleXmlTree
import binascii
import random
import string


class MetaVarSpecParser(object):

    def __init__(self, xmlfile, seed=None):

        self.realvars = []
        self.metavars = []

        xml = SimpleXmlTree.SimpleXmlTree(xmlfile)
        # print xml

        # Populate our ordered dictionary
        tracer = MetaVarSpecTracer(self.metavars)
        tracer.visit(xml.getRoot())

        #print self
        #print self.getRandom()

        if seed is not None:
            random.seed(seed)

    def __str__(self):
        s = ""
        for mv in self.metavars:
            s += "%s\n"%(mv)
        return s


    def getRandom(self):
        s = ""
        for mv in self.metavars:
            s += "%s "%(mv.getRandomValAsStr())
        return s


    def generateRandom(self, outfile, count):
        if os.path.isfile(outfile):
            raise IOError("Error: output file already exists: %s"%(outfile))
        f = open(outfile, 'w') 
        for i in range(1, (count + 1)):
            f.write(self.getRandom() + "\n") 
        f.close()



    def processRealVars(self, infile):
        if not os.path.isfile(infile):
            raise IOError("Error: input file not found: %s"%(infile))
        
        f = open(infile, 'r') 
        lines1 = f.readlines()
        f.close()
            
        for line1 in lines1:
            line = line1.strip()
            if ( len(line) > 0 ) and ( not line.startswith('#') ):   
                self.realvars.append(self.processRealVarsStr(line))

  
    def processRealVarsStr(self, vars_str):
        l_v = []
        l_cv = vars_str.split()
        
        if len(l_cv) != len(self.metavars):
            raise ValueError("Error: expecting %d vars, got %d: %s"%(len(self.metavars), len(l_cv), vars_str))

        i = 0
        for cv in l_cv:
            mv = self.metavars[i]
            v = mv.str2Val(cv, mv.var_t)
            l_v.append(v)
            i += 1

        return l_v

##########################################################################################################################


class MetaVariable(object):

    def __init__(self, name):
        # Variable name:
        self.var_n = name
        # Variable type:
        self.var_t = None
        # Default value:
        self.var_v = None
        # Minimum value:
        self.var_min = None
        # Maximum value:
        self.var_max = None



    def __str__(self):
        s = ""
        
        s += "name: %s type:%s "%(self.var_n, self.type2Str(self.var_t))

        if self.var_min is not None:
            s += "min:%d "%(self.var_min)

        if self.var_max is not None:
            s += "max:%d "%(self.var_max)

        if self.var_v is not None:
            s += "default:%s"%(self.val2Str(self.var_v))
        
        return s 

       
    def initType(self, s):
        self.var_t = self.str2Type(s)
        if self.var_t is None:
            raise ValueError("Error: metavar %s: invalid 'type' value: %s"%(self.var_n, s))

    def initVal(self, s, t):
        v = self.str2Val(s, t)
        if v is None:           
            raise ValueError("Error: metavar %s: invalid default value provided: %s"%(self.var_n, s))
        self.var_v = v


    def initMin(self, n):
        self.var_min = int(n)
        if (self.var_max is not None) and (self.var_min > self.var_max):
            raise ValueError("Error: metavar %s: 'min' value exceeds 'max': %d"%(self.var_n, self.var_min))

    def initMax(self, n):
        self.var_max = int(n) 
        if (self.var_min is not None) and (self.var_max < self.var_min):
            raise ValueError("Error: metavar %s: 'max' value is less than 'min': %d"%(self.var_n, self.var_max))


    def val2Str(self, v):
        if self.isInt(type(v)):
            return "%d"%(v)
        elif self.isBool(type(v)):
            if v is True:
                return "1"
            else:
                return "0"
        elif self.isStr(type(v)):
            return v
        elif self.isByteArray(type(v)):
            return "%s"%(binascii.hexlify(bytearray(v)))
        else:
            return None

    def str2Val(self, s, t):
        if self.isInt(t):
            if (self.var_min is not None) and (int(s) < self.var_min):
                raise ValueError("Error: metavar %s: value %d is less than min: %d"%(self.var_n, int(s), self.var_min))
            if (self.var_max is not None) and (int(s) > self.var_max):
                raise ValueError("Error: metavar %s: value %d is greater than max: %d"%(self.var_n, int(s), self.var_max))
            return int(s)
        elif self.isBool(t):
            if s == '0':
                return False
            else:
                return True
        elif self.isStr(t):
            if (self.var_min is not None) and (len(s) < self.var_min):
                raise ValueError("Error: metavar %s: length of %s is less than min: %d"%(self.var_n, s, self.var_min))
            if (self.var_max is not None) and (len(s) > self.var_max):
                raise ValueError("Error: metavar %s: length of %s is greater than max: %d"%(self.var_n, s, self.var_max))
            return s
        # Use this for hex string
        elif self.isByteArray(t):
            if (self.var_min is not None) and (len(s) < (2 * self.var_min)):
                raise ValueError("Error: metavar %s: byte-length %s is less than min: %d"%(self.var_n, s, self.var_min))
            if (self.var_max is not None) and (len(s) > (2 * self.var_max)):
                raise ValueError("Error: metavar %s: byte-length of %s is greater than max: %d"%(self.var_n, s, self.var_max))
            if len(s) % 2:
                raise ValueError("Error: metavar %s: odd-length bytearray string: %s"%(self.var_n, s))
            # Can raise ValueError:
            return bytearray.fromhex(s)
        else:
            return None


    def str2Type(self, s):
        if s == 'int':
            return int
        elif s == 'bool':
            return bool
        elif s == 'str':
            return str
        # Use this for hex string
        elif s == 'bytearray':
            return bytearray
        else:
            return None

    def type2Str(self, t):
        if self.isInt(t):
            return 'int'
        elif self.isBool(t):
            return 'bool'
        elif self.isStr(t):
            return 'str'
        # Use this for hex string
        elif self.isByteArray(t):
            return 'bytearray'
        else:
            return None


    def isStr(self, t):
        return (t == str)

    def isInt(self, t):
        return (t == int)

    def isBool(self, t):
        return (t == bool)

    def isByteArray(self, t):
        return (t == bytearray)


    def getRandomVal(self):
        if not self.isBool(self.var_t):
            if (None is self.var_min) or (None is self.var_max):
                raise ValueError("Error: metavar %s: no 'min' and/or 'max' limitations have been defined"%(self.var_n, self.var_max))
        if self.isInt(self.var_t):
            # INCLUSIVE of BOTH min and max
            return random.randint(self.var_min, self.var_max)
        elif self.isBool(self.var_t):
            return bool(random.randint(0, 1))
        elif self.isStr(self.var_t):
            return ''.join([random.choice(string.ascii_letters + string.digits + string.punctuation) for n in range(random.randint(self.var_min, self.var_max))])
        elif self.isByteArray(self.var_t):
            return bytearray.fromhex(''.join([random.choice(string.hexdigits) for n in range(2 * random.randint(self.var_min, self.var_max))]))
        else:
            raise ValueError("Error: metavar %s: type unknown"%(self.var_n, self.var_max))

    def getRandomValAsStr(self):
        return self.val2Str(self.getRandomVal())

##########################################################################################################################

# A sample tree visitor implementation for debugging purposes:

class MetaVarSpecTracer(SimpleXmlTree.XmlTreeVisitor):

    def __init__(self, metavars):
        self.metavars = metavars
        self.index = 0
        # Invoke the super (XmlTreeVisitor) class constructor:
        super(MetaVarSpecTracer, self).__init__(SimpleXmlTree.XmlTreeVisitorType.breadthfirst)

    def previsit_breadthfirst(self, node): 
        if not node.isRoot():

            # Take for example this node which 'specifies' our variable: <MYINTEGER min=20 max=40 type='int'> 25 </MYINTEGER>
            # Required is the name of the variable (MYINTEGER), and its type ('int'). 
            # Everything else is optional.

            if node.isParent():
                # Meta variables spec in XML should be FLAT
                raise ValueError("Error: not valid xml for meta-variables specification")
            else:
                # k == MYINTEGER (the name of the variable we are specifying) 
                k = node.getTag()
                for mv in self.metavars:
                    if k == mv.var_n:
                        # Make sure there isn't already a variable called MYINTEGER
                        raise ValueError("Error: meta-variable already defined: %s"%(k))

                mv = MetaVariable(k)

                for a in node.getAttrib():
                                                      
                    if a == 'type':
                        mv.initType(node.getAttribVal(a))
                
                    # Min/Max will refer to str length where appropriate
                    elif a == 'min':
                        mv.initMin(node.getAttribVal(a))
                    elif a == 'max':
                        mv.initMax(node.getAttribVal(a))

                    else:
                        raise ValueError("Error: unsupported xml attribute: %s"%(a))
                
                if mv.var_t is None:
                    raise ValueError("Error: 'type' attribute not specified: %s"%(k))
                
                if node.hasVal():
                    mv.initVal(node.getVal(), mv.var_t)
       
                self.metavars.append(mv)
                     


