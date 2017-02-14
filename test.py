#!/usr/bin/python
# -*- coding: UTF-8 -*-
from afftranslator2 import *

affs = ["II. Institut Theoretische Physik - Hamburger Universitat - Luruper Chausse - Hamburg - Germany", "Orsay LAL",
        "LMU Munich, Germany, 53706-1534 madi", 
        "Krabbelgruppe 'Schneewittchen' - Maerchenkindergarten - Hamburg", 
        "Universitat Greifswald, 17487 Greifswald and Center for Advanced Mathematics and Physics Islamabad and Perimeter Institute, Waterloo", 
        "Corresponding authors"]

for aff in affs:
    print 'What is the ICN for the affiliation "%s"?' % (aff)
    #bm = bestmatch(aff,'ICN',onlycore=True)
    bm = bestmatch(aff,'ICN',old=True)
    for i in range(min(10,len(bm))):
        print "   ",bm[i]
    print 'afftranslator would suggest the ICN "%s" for "%s".' % (bm[0][1], aff)
    print 'This suggestion reached the score %6.4f (from %6.4f possible).\n\n' % (bm[0][0], bm[0][2])

