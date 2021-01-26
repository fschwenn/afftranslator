#!/usr/bin/python

import time
from afftranslator2 import *

starttime = time.clock()


#generateknowledgebase('aff-translator-old.pickle',True)
generateknowledgebase('aff-translator.pickle',True)
#generateknowledgebase('aff-translator.pickle',False)


stoptime = time.clock()

print stoptime-starttime,"seconds"

