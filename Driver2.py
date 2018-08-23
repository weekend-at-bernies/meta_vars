import os.path
import sys
import MetaVars
import argparse

parser = argparse.ArgumentParser(description='PhantomVars tester')
parser.add_argument('-i','--input', help='Input file (xml meta-var spec)', required=True, metavar='<input file>')
parser.add_argument('-o','--output', help='Output file (randomized var output)', required=True, metavar='<output file>')
parser.add_argument('-s','--seed', help='randomizer seed', required=False, metavar='<seed>')
parser.add_argument('-n','--count', help='output var count', required=True, metavar='<count>')
args = vars(parser.parse_args())

if args['seed'] is not None:
    seed = int(args['seed'])
else:
    seed = None

mv = MetaVars.MetaVarSpecParser(args['input'], seed)
mv.generateRandom(args['output'], int(args['count']))



