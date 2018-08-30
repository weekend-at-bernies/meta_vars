import os.path
import sys
import MetaVars
import argparse

parser = argparse.ArgumentParser(description='MetaVars tester')
parser.add_argument('-1','--xml1', help='XML meta-vars specification file', required=True, metavar='<xml file 1>')
parser.add_argument('-2','--xml2', help='XML data sort specification file', required=True, metavar='<xml file 2>')
parser.add_argument('-i','--input', help='Input data file', required=True, metavar='<input file>')
parser.add_argument('-o','--output', help='Output directory (cannot already exist)', required=True, metavar='<output dir>')
args = vars(parser.parse_args())

mv = MetaVars.MetaVariableProcessor(args['xml1'])
mv.createOrder(args['input'], args['output'], args['xml2'])
print "all done!"



