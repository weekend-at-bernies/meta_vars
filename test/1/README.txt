'test1.data' generated like this:
$ python Driver1.py -i mvspec.xml -o test1.data -s 5000 -n 100

Directory 'out' generated like this:
$ python Driver2.py -1 mvspec.xml -2 dataspec.xml -i test1.data -o out

'out.hash' generated like this (you may need to apt-install 'hashdeep' first):
$ hashdeep -rlc md5 out > out.hash
