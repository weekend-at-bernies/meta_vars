import os.path
import sys
import SimpleXmlTree
import binascii
import random
import string
import operator
import WorkerManager
from WorkerManager import WorkerType
from WorkerManager import WorkerStatus

class MetaVariableProcessor(object):

    # IN: 'xmlfile' : specification of a set of meta variables (ordered)
    # IN: 'seed' : randomizer seed
    def __init__(self, xmlfile):

        # Will raise exception if syntax errors found:
        xml = SimpleXmlTree.SimpleXmlTree(xmlfile)
        # print xml

        tracer = MetaVarXMLSpecTracer()

        # Will raise exception if semantic errors found:
        tracer.visit(xml.getRoot())

        self.mv_bin = MetaVariableBin(tracer.l_mv)

        #print self
        #print self.getRandom()
      
    def __str__(self):
        return str(self.mv_bin)


    def getRandomBinAsStr(self):
        return self.mv_bin.getRandomAsStr()

    def getRandomBinAsVal(self):
        return self.mv_bin.getRandomAsVal()




    # IN: a text file where each line represents a MetaVariable bin, eg:
    #         "1 5 yo ..."
    #         "70 2 blah ..."
    #         "0 0 foo ..."
    # OUT: returns a list of a MetaVariable bins:
    #         [[1, 5, "yo", ...],
    #          [70, 2, "blah", ...],
    #          [0, 0, "foo", ...],
    def getBinsFromFile(self, infile):
        if not os.path.isfile(infile):
            raise IOError("Error: input file not found: %s"%(infile))
        
        f = open(infile, 'r') 
        lines = f.readlines()
        f.close()
            
        l_bin = []
        for line in lines:
            line = line.strip()
            if ( len(line) > 0 ) and ( not line.startswith('#') ):   
                l_v = self.mv_bin.str2Vals(line.split())
                if l_v is not None:
                    l_bin.append(l_v)
                else:
                    raise ValueError("Error: could not process: %s"%(line))
        return l_bin

    


    # Outputs a file where each line represents a randomized MetaVariable bin, eg:
    #         "1 5 yo ..."
    #         "70 2 blah ..."
    #         "0 0 foo ..."
    #
    # IN: 'outfile' : output file (can't exist)
    # IN: 'count' : the number of lines to output
    def createRandomsFile(self, outfile, count, seed=None):
        if seed is not None:
            random.seed(seed)
        if os.path.isfile(outfile):
            raise IOError("Error: output file already exists: %s"%(outfile))
        f = open(outfile, 'w') 
        for i in range(1, (count + 1)):
            f.write((" ").join(self.getRandomBinAsStr()) + "\n")
        f.close()


     
    # IN: 'infile' : input file where each line is a MetaVariable bin, eg:
    #         "1 5 yo ..."
    #         "70 2 blah ..."
    #         "0 0 foo ..."
    #
    # IN: 'outdir' : output directory (can't exist) where to dump ordered MetaVariable bins
    # IN: 'xmlorderspec' : specification of how to order the MetaVariable bins
    def createOrder(self, infile, outdir, xmlorderspec):
        if os.path.isdir(outdir):
            raise IOError("Error: output directory already exists: %s"%(outdir))
        l_bin = self.getBinsFromFile(infile)
        
        # Will raise exception if there are syntax errors:
        xml = SimpleXmlTree.SimpleXmlTree(xmlorderspec)
        # print xml

        # Semantic checker:
        # Will raise exception if there are semantic errors:
        checker = MetaVarBinsXMLOrderSpecChecker(self.mv_bin)
        checker.visit(xml.getRoot())

        yyyy = YYYYVisitor(self.mv_bin, l_bin, outdir)
        yyyy.visit(xml.getRoot())

        #tracer = DataSortSpecVisitor(self.l_mv, l_rv, outdir, True)
        #tracer.visit(xml.getRoot())
        


    

##########################################################################################################################

# A bin of unique MetaVariables (basically an abstraction over a list of MetaVariable objects)
class MetaVariableBin(object):

    # IN: a list of MetaVariable objects (the bin)
    def __init__(self, l_mv):
        self.l_mv = l_mv

    def __str__(self):
        s = ""
        for mv in self.l_mv:
            s += "%s\n"%(mv)
        return s


    # IN: list of MetaVariables as strings: ["1", "5", "yo", ..."]
    # OUT: list of MetaVariables as their proper types: [1, 5, "yo", ...]
    def str2Vals(self, l_s):  
        if len(l_s) != len(self.l_mv):
            return None
        l_v = []
        i = 0
        for s in l_s:
            mv = self.l_mv[i]
            l_v.append(mv.str2Val(s, mv.var_t))
            i += 1
        return l_v

    # IN: list of MetaVariables as their proper types: [1, 5, "yo", ...]
    # OUT: list of MetaVariables as strings: ["1", "5", "yo", ..."]
    def vals2Str(self, l_v):
        if len(l_v) != len(self.l_mv):
            return None
        l_s = []
        i = 0     
        for v in l_v:
            l_s.append(self.l_mv[i].val2Str(v))
            i += 1
        return l_s

    # Returns randomized list of MetaVariables as strings: ["1", "5", "yo", ..."]
    def getRandomAsStr(self):
        l_s = []
        for mv in self.l_mv:
            l_s.append(mv.getRandomAsStr())
        return l_s

    # Returns randomized list of MetaVariables as their proper types: [1, 5, "yo", ...]
    def getRandomAsVal(self):
        l_v = []
        for mv in self.l_mv:
            l_v.append(mv.getRandomAsVal())
        return l_v


    # Returns the 0-based index of MetaVariable in the bin
    # given its name
    def get_mv_idx(self, var_n):
        i = 0
        for mv in self.l_mv:
            if mv.var_n == var_n:
                return i
            i+=1
        return -1
   
##########################################################################################################################

# A single MetaVariable
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


    def getRandomAsVal(self):
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

    def getRandomAsStr(self):
        return self.val2Str(self.getRandomAsVal())

##########################################################################################################################

# traces input mv spec

class MetaVarXMLSpecTracer(SimpleXmlTree.XmlTreeVisitor):

    def __init__(self):
        self.l_mv = []
        self.index = 0
        # Invoke the super (XmlTreeVisitor) class constructor:
        super(MetaVarXMLSpecTracer, self).__init__(SimpleXmlTree.XmlTreeVisitorType.breadthfirst)

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
                for mv in self.l_mv:
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
                
                if len(node.getVal()) > 0:
                    mv.initVal(node.getVal(), mv.var_t)
       
                self.l_mv.append(mv)


##########################################################################################################################

# Performs semantic check only over XML
class MetaVarBinsXMLOrderSpecChecker(SimpleXmlTree.XmlTreeVisitor):

    def __init__(self, mv_bin):
        self.mv_bin = mv_bin

        # Invoke the super (XmlTreeVisitor) class constructor:
        super(MetaVarBinsXMLOrderSpecChecker, self).__init__(SimpleXmlTree.XmlTreeVisitorType.depthfirst)


    def previsit_depthfirst(self, node): 

        if not node.isRoot():
           # print "PRE: %s"%(node)
            if self.mv_bin.get_mv_idx(node.getTag()) < 0:
                raise ValueError("Error: unknown meta-variable: %s"%(node.getTag()))            

            for a in node.getAttrib():                                                  
                if a == 'type':
                    a_v = node.getAttribVal(a)
                    if a_v == 'bin':
                        pass
                    elif a_v == 'sort':
                        pass
                    else:
                        raise ValueError("Error: unsupported xml attribute value: type='%s'"%(a_v))               
                else:
                    raise ValueError("Error: unsupported xml attribute: %s"%(a))

    def postvisit_depthfirst(self, node): 
        #print "POST: %s"%(node)
        pass

# Example:
#
#PRE: <cellId type='bin'></cellId>
#PRE: <rnti type='bin'></rnti>
#PRE: <fullSampleIdx type='sort'></fullSampleIdx>
#POST: <fullSampleIdx type='sort'></fullSampleIdx>
#PRE: <fileSampleIdx type='sort'></fileSampleIdx>
#POST: <fileSampleIdx type='sort'></fileSampleIdx>
#POST: <rnti type='bin'></rnti>
#PRE: <prb_offset type='bin'></prb_offset>
#PRE: <n_prb type='bin'></n_prb>
#PRE: <fullSampleIdx type='sort'></fullSampleIdx>
#POST: <fullSampleIdx type='sort'></fullSampleIdx>
#PRE: <fileSampleIdx type='sort'></fileSampleIdx>
#POST: <fileSampleIdx type='sort'></fileSampleIdx>
#POST: <n_prb type='bin'></n_prb>
#POST: <prb_offset type='bin'></prb_offset>
#PRE: <TBS type='bin'></TBS>
#PRE: <prb_offset type='bin'></prb_offset>
#PRE: <n_prb type='bin'></n_prb>
#PRE: <fullSampleIdx type='sort'></fullSampleIdx>
#POST: <fullSampleIdx type='sort'></fullSampleIdx>
#PRE: <fileSampleIdx type='sort'></fileSampleIdx>
#POST: <fileSampleIdx type='sort'></fileSampleIdx>
#POST: <n_prb type='bin'></n_prb>
#POST: <prb_offset type='bin'></prb_offset>
#POST: <TBS type='bin'></TBS>
#POST: <cellId type='bin'></cellId>


##########################################################################################################################



# BLAH
class YYYYVisitor(SimpleXmlTree.XmlTreeVisitor):

    def __init__(self, mv_bin, l_bin, outdir):
        self.mv_bin = mv_bin
        self.curr_l_bin = l_bin
        self.curr_outdir = outdir

        self.target_node = None

        super(YYYYVisitor, self).__init__(SimpleXmlTree.XmlTreeVisitorType.breadthfirst)



    def previsit_breadthfirst(self, node): 

        
        
        if node.isRoot():
            self.target_node = node

       # print "CURRENT: %s | TARGET: %s"%(node, self.target_node)
       # print id(node)
       # print id(self.target_node)
        if self.target_node == node:
           # print "%d: GOT TARGET: %s"%(os.getpid(), node)
            if node.isParent():
                #print "PARENT: %s"%(node)
                pass
            if not node.isParent():
                print "%d: %s"%(os.getpid(), node.getLineage())

            notforked = True
            i = 0
            for c in node:
                if i == 0:
                    myidx = 0
                else:
                    if notforked:
                       # print "%d: FORKING!"%(os.getpid())
                        newpid = os.fork()
                        if newpid == 0:
                            # This is the forked/child process
                            myidx = i
                        else:
                            notforked = False
                i += 1

         
            i = 0
            for c in node:
                if i == myidx:  
                   # print "%d: NEXT TARGET: %s"%(os.getpid(), c)
                   # print id(c)
                    self.target_node = c
                i += 1
    




    
               





##########################################################################################################################



# BLAH
class XXXXVisitor(SimpleXmlTree.XmlTreeVisitor):

    def __init__(self, mv_bin, l_bin, outdir):
        self.mv_bin = mv_bin
        self.curr_l_bin = l_bin
        self.curr_outdir = outdir

        super(XXXXVisitor, self).__init__(SimpleXmlTree.XmlTreeVisitorType.depthfirst)



    # IN: l_bin: a list of MetaVariable bins:
    #            [[1, 5, "yo", ...],         
    #             [70, 2, "blah", ...],
    #             [0, 0, "foo", ...],
    #
    # PURPOSE: split l_bin into bins of equivalent: bin[mv_idx]
    #
    # OUT: d_l_bin{ key=mv[mv_idx] } returns l_bin
    #
    def genBinsDict(self, l_bin, mv_idx):       
        #node.bins = []
        d_l_bin = {}
        for b in l_bin:
            if b[mv_idx] in d_l_bin:
                (d_l_bin[b[mv_idx]]).append(b)
            else:
                d_l_bin[b[mv_idx]] = [b]
        return d_l_bin


    def doPreBinWork(self, mv_idx):
        
        # Now we are free to blow away self.data:
        d_l_bin = self.genBinsDict(self.curr_l_bin, mv_idx)
        
        # FORK PROCESS len(d_l_bin) times
        for k in d_l_bin:
            newpid = os.fork()
            if newpid == 0:
                continue
            else:
                self.curr_l_bin = d_l_bin[k]
                self.curr_outdir = None #fixme
                break



    def doPreSortWork(self, mv_idx):
        # ASCENDING (invoke 'sorted(... , doReverse=True)' for descending order)
        self.curr_l_bin = sorted(self.curr_l_bin, key=operator.itemgetter(mv_idx))


    def previsit_depthfirst(self, node): 
        if not node.isRoot():
           # print "PRE: %s"%(node)
            mv_idx = self.mv_bin.get_mv_idx(node.getTag())
            if mv_idx < 0:
                raise ValueError("Error: unknown meta-var: %s"%(node.getTag()))            

            for a in node.getAttrib():                                                  
                if a == 'type':
                    a_v = node.getAttribVal(a)
                    if a_v == 'bin':                       
                        self.doPreBinWork(mv_idx)
                    elif a_v == 'sort':
                        self.doPreSortWork(mv_idx)
                    else:
                        raise ValueError("Error: unsupported xml attribute value: type='%s'"%(a_v))
                   
                 


                    #if node.isParent():
                    #    if not a_v == 'bin':
                    #        raise ValueError("Error: unsupported xml attribute value: %s='%s'"%(a, a_v))   
                    #    if not self.semanticOnly:
                    #        self.assignBins(l_rv_idx)
                    #else:
                    #    if not a_v == 'sort':
                    #        raise ValueError("Error: unsupported xml attribute value: %s='%s'"%(a, a_v))   
                    #    if not self.semanticOnly:
                    #        self.sortBin(l_rv_idx)                 
                else:
                    raise ValueError("Error: unsupported xml attribute: %s"%(a))

    #def postvisit_depthfirst(self, node): 
    #    print node
    #    pass




# This extends the WorkerManager.WorkerManager class:
class MyWorkerManager(WorkerManager.WorkerManager):

    def __init__(self, workercount, workertype):
        # Invoke the super (WorkerManager.WorkerManager) class constructor:
        super(MyWorkerManager, self).__init__(workertype)

        for i in range(0, workercount):
            noun = nouns[random.randint(0, (len(nouns) - 1))]
            adjective = adjectives[random.randint(0, (len(adjectives) - 1))]

            # Create a worker:
            myworker = MyWorker((adjective + noun))

            # Schedule the worker with its work function and static args:
            args = [random.randint(0, 100)]
            self.scheduleWorker(myworker, myworker.work, args)

    def run(self):

        # Start the workers:
        self.startWorkers()

        # Join the workers:
        if not self.joinWorkers():
            raise AssertionError("Not all workers have completed without error.")

        return self.getDuration()


# This extends the WorkerManager.Worker class:
class MyWorker(WorkerManager.Worker):

    # 'rtargs' : run-time args (as opposed to the static args specified at schedule-time)
    def work(self, rtargs):
        # Mandatory:
        self.prework()

        # Insert your work here:
        pass

        # Mandatory:   
        self.postwork(WorkerStatus.completed_success) 
               
    def __init__(self, identity):
        # Invoke the super (WorkerManager.Worker) class constructor:
        super(MyWorker, self).__init__()
        self.identity = identity

##########################################################################################################################

# A sample tree visitor implementation for debugging purposes:

# SEMANTIC CHECK ONLY
class DataSortSpecVisitor(SimpleXmlTree.XmlTreeVisitor):

    def __init__(self, metavars, l_rv, outdir, semanticOnly):
        self.stack = []
        self.data = l_rv
        self.l_mv = metavars
        self.semanticOnly = semanticOnly

        #if not semanticOnly:          
        #    self.stack.append(l_rv)
            #self.fs = {}
            #self.current_fs = None

            #self.outdir_stack = []
            #self.l_rv_stack = []
            #self.l_rv_stack.append(l_mv)
            #self.outdir_stack.append(outdir)

        # Invoke the super (XmlTreeVisitor) class constructor:
        super(DataSortSpecVisitor, self).__init__(SimpleXmlTree.XmlTreeVisitorType.depthfirst)

        # Stack: data bins:
        # zzz

    

    # IN: l_rv: a list of real vars:
    #            [[1, 5, "yo", ...],          <--- a single rv
    #             [70, 2, "blah", ...],
    #             [0, 0, "foo", ...],
    #
    # Sort l_rv by ascending rv[rv_idx]
    #
    # OUT: l_rv_sorted: [rv0, rv1, rv2 ...] 
    #
    def doSort(self, l_rv, rv_idx):
        # ASCENDING (invoke 'sorted(... , doReverse=True)' for descending order)
        return sorted(l_rv, key=operator.itemgetter(rv_idx))


    # IN: l_rv: a list of rv:
    #            [[1, 5, "yo", ...],          <--- a single rv
    #             [70, 2, "blah", ...],
    #             [0, 0, "foo", ...],
    #
    # Split l_rv into bins of equivalent: rv[rv_idx]
    #
    # OUT: bins{rv[rv_idx]} returns [rv, rv, rv ...]
    #
    def createBins(self, l_rv, rv_idx):       
        #node.bins = []
        bins = {}
        for rv in l_rv:
            if rv[rv_idx] in bins:
                (bins[rv[rv_idx]]).append(rv)
            else:
                bins[rv[rv_idx]] = [rv]
        return bins
        #for k in bins:
        #    node.bins.append(bins[k])        


    # Does the input data represent a bin of rvs?
    #            [[1, 5, "yo", ...],          <--- a single rv
    #             [70, 2, "blah", ...],
    #             [0, 0, "foo", ...], 
    #
    def is_l_rv(self, data):
        if type(data) is list:
           if len(data) > 0:
               if type(data[0]) is list:
                   return True
        return False


    def doPreSortWork(self, rv_idx):
        data = self.stack.pop()
 
    
    def doPreBinWork(self, rv_idx):
        # Push a copy of self.data onto stack:
        self.stack.append(self.data)
        
        # Now we are free to blow away self.data:
        bins = self.createBins(data, rv_idx)
         

        #data = self.stack.pop()
        # 1st bin
        # bin inside bin
        # bin inside sort
        #if type(data) is list:
        #    bins = self.createBins(data, rv_idx)
        #elif type(data) is dict:
            
 
        
 




    def previsit_depthfirst(self, node): 


        if not node.isRoot():
           # print "PRE: %s"%(node)
            rv_idx = self.get_rv_idx(node.getTag())
            if rv_idx < 0:
                raise ValueError("Error: unknown meta-var: %s"%(node.getTag()))            

            for a in node.getAttrib():                                                  
                if a == 'type':
                    a_v = node.getAttribVal(a)
                    if a_v == 'bin':
                        if not self.semanticOnly:
                            self.doPreBinWork(rv_idx)
                    elif a_v == 'sort':
                        if not self.semanticOnly:
                            self.doPreSortWork(rv_idx)
                    else:
                        raise ValueError("Error: unsupported xml attribute value: type='%s'"%(a_v))
                   
                 


                    #if node.isParent():
                    #    if not a_v == 'bin':
                    #        raise ValueError("Error: unsupported xml attribute value: %s='%s'"%(a, a_v))   
                    #    if not self.semanticOnly:
                    #        self.assignBins(l_rv_idx)
                    #else:
                    #    if not a_v == 'sort':
                    #        raise ValueError("Error: unsupported xml attribute value: %s='%s'"%(a, a_v))   
                    #    if not self.semanticOnly:
                    #        self.sortBin(l_rv_idx)                 
                else:
                    raise ValueError("Error: unsupported xml attribute: %s"%(a))

    def postvisit_depthfirst(self, node): 
        if not node.isRoot():
            #print "POST: %s"%(node)
            for a in node.getAttrib():                                                  
                if node.getAttribVal(a) == 'bin':
                    l_rv = self.l_rv_stack.pop()
                    self.outdir_stack.pop()

    def get_rv_idx(self, var_n):
        i = 0
        for mv in self.l_mv:
            if mv.var_n == var_n:
                return i
            i+=1
        return -1

    #def has_mv(self, k):
    #    if self.get_l_rv_idx(k) < 0:
    #        return False
    #    return True
        

                     


