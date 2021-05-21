# -*- coding: UTF-8 -*-
#!/usr/bin/python
#

import re
import sys
import os
import unicodedata
import cPickle
#from unidecode import unidecode
#from invenio.search_engine import search_pattern
#from invenio.search_engine import get_most_popular_field_values
#from invenio.search_engine import get_fieldvalues
#from invenio.search_engine import get_record
#from invenio.search_engine import get_collection_reclist
from inspirelabslib import *
from sets import Set
import urllib3
import time

urllib3.disable_warnings()

#settings
knowledgebasepath = "/afs/desy.de/user/l/library/proc/aff-translation"
#knowledgebasepath = "/afs/cern.ch/user/s/sachs/w0/inspire/aff-translation"

#different variants in city writing
particles =[["De", "de"], ["La", "la"], ["Ley", "ley"], ["Do", "do"], ["I", "i"], ["El", "el"], ["Di", "di"], ["On", "on"], ["Es", "es"], ["Am", "am"], ["Del", "del"], ["Sur", "sur"], ["Dos", "dos"], ["Lez", "lez"], ["Les", "les"], ["Saint", "St."], ["Sainte", "Ste."]]
#make rather regular expression in afftranslator case insenseitive
particles =[["Saint", "St."], ["Sainte", "Ste."], ["St","St."]]

#precompiled regular expressions
regexpserbia = re.compile('(?i)Serbia and Montenegro')
regexpsemilonseperator = re.compile(';   ')
regexpsemikolonicns = re.compile(' *; *')
regexptrainlingsemikolon = re.compile(';$')
regexpunlistedus = re.compile('Unlisted, US, ')
regexpstartingspace = re.compile('^ *\-')
regexptrailingspace = re.compile('\- *$')
regexpspaceordash = re.compile('[ \-]')
regexptrailingcomma = re.compile(', *$')
regexpaddress = re.compile('.*([A-Z]+)( |\-)([A-Z]+)$')
regexpcc = re.compile('.* ([A-Z]+)$')
regexpunlisted = re.compile('^Unlisted')
regexpszet = re.compile(u'ß')

#only new affiliations
newaffdict = {}
oldicns = []

def crossloop(sequences):
    result = [[]]
    for seq in sequences:
        result = [sublist + [item] for sublist in result for item in seq]
    return result

def not_combining(char):
    return unicodedata.category(char) != 'Mn'

def strip_accents(text):
#        unicode_text= unicodedata.normalize('NFD', text.decode(encoding))
#        unicode_text= unicodedata.normalize('NFD', text)
    normalizedstring = unicodedata.normalize('NFKD', re.sub(u'ß', u'ss', text))
    return unicode(normalizedstring.encode('ascii', 'ignore'), 'utf-8')

    
#unicode_text= unicodedata.normalize('NFD', text.decode('utf-8'))
#return filter(not_combining, unicode_text).encode('ASCII','ignore')

def adfiwrite(affline, afflineappendix):
    affline = regexpserbia.sub('Serbia', affline) + afflineappendix
    afflinestripped = strip_accents(affline)
    try:
        adfi.write(affline)
        rawversionwritten = True
    except:
        rawversionwritten = False        
    if not rawversionwritten or not afflinestripped == affline:
        adfi.write(afflinestripped) 
    return
def adfioldwrite(affline, afflineappendix):
    affline = regexpserbia.sub('Serbia', affline) + afflineappendix
    afflinestripped = strip_accents(affline)
    try:
        adfiold.write(affline)
        rawversionwritten = True
    except:
        rawversionwritten = False      
    if not rawversionwritten or not afflinestripped == affline:
        adfiold.write(afflinestripped) 
    return


dludict={}
def tgstrip(x): return x.strip()
#informations from SPIRES
databasefil = open(knowledgebasepath+'/aff-dlu-from-inst.bas.ccc.promoted')
databaseentries = map(tgstrip, databasefil.readlines())
databasefil.close()
for entry in databaseentries:
    if not  re.search('^#',entry):
         parts = regexpsemilonseperator.split(entry, maxsplit=4)
         icn = parts[1]
         dlu = parts[2]
         #if not dlu == 'NONE': dludict[icn]=dlu
         dludict[icn]=dlu
#informations from repinst
databasefil = open('/afs/desy.de/user/l/library/lists/repinst')
databaseentries = map(tgstrip, databasefil.readlines())
databasefil.close()
for entry in databaseentries:    
    #entry = re.sub('(.*?;.*?);.*',r'\1',entry)
    #dlu = re.sub(';.*','',entry)
    #icn = re.sub('.*; ', '', entry)
    parts = regexpsemikolonicns.split(entry)
    if len(parts) > 1:
        dlu = parts[0]
        icn = regexptrainlingsemikolon.sub('', parts[1])
        dludict[icn]=dlu
    else:
        print 'wrong entry in repinst:',entry
    


#adfiold = open(knowledgebasepath+'/aff-dlu-from-inspire-old.afb', 'w')
#adfiold.write('# affiliation -> dlu database from INST database of INSPIRE (with old institutes)\n')



countriescc = {}
normcities = {}
#informations from INSPIRE
#institutes = search_pattern(p="980__a:INSTITUTION  not 980:DELETED not 001:910325 not 001:910584")
#institutes = search_pattern(p="980__a:INSTITUTION  not 980:DELETED not 980:DEAD not 001:910325 not 001:910584 and not 510__w:b")
institutes = get_recids("United", collection="institutions")+get_recids("!United", collection="institutions")
print len(institutes),'institutes found'


i = 0
for recid in institutes:
    time.sleep(1)
    i += 1
    if i % 1 == 0: 
        print ' --- %i/%i --- %i ---' % (i, len(institutes), recid)
    institute = get_inspire_record(recid, collection="institutions")
    print institute
    if not 'legacy_ICN' in institute.keys():
        print '!', recid
        continue
    #else:
    affapplines = []
    #identifiers
    icn = institute['legacy_ICN']
    if regexpunlistedus.search(icn):
        continue
    try:
        newicn = institute['legacy_ICN']
    except:
        newicn = ''
    try:
        orgt = institute['institution_hierarchy'][0]
        organization = orgt['name']
        if 'acronym' in orgt.keys() and orgt['acronym']:
            organization += ' (%s)' % (orgt['acronym'])
    except:
        organization = ''
    try:
        dept = institute['institution_hierarchy'][1]
        department = dept['name']
        if 'acronym' in dept.keys() and dept['acronym']:
            department += ' (%s)' % (dept['acronym'])
    except:
        department = ''
    dlu = ''
    #coreness
    core = ';   ;'
    if 'core' in institute.keys() and institute['core']:
        core = ';   CORE;'            
    #DLU
    #
    # no longer in database
    #
    #GRID
    grid = '   ;\n'
    if 'external_system_identifiers' in institute.keys():
        for idt in institute['external_system_identifiers']:
            if idt['schema'] == 'GRID':
                grid = '   %s;\n' % (idt['value'])
    #print ' ICN=',icn
    #print ' NEWICN=',newicn
    #print ' DLU=', dlu
    if icn == '':
        print recid, ' no ICN'
        #icn = newicn
        #print recid, ' no ICN and no NEWICN'
    elif dlu == '':
        if dludict.has_key(icn):
            dlu = dludict[icn]
        else:
            #print recid, icn, 'missing DLU !'
            dlu = "NONE"
    elif dludict.has_key(icn):
        if dlu !=  dludict[icn]:
            print recid, 'ICN=',icn,' --> '+dlu+' != '+ dludict[icn]," (DLU conflict)"  
            dludict[icn] = dlu
    if 'addresses' in institute.keys():
        for dreisiebeneins in institute['addresses']:
            (country, city, plz, address) = ('', '', '', '')
            if 'country_code' in dreisiebeneins.keys():
                cc = dreisiebeneins['country_code']
            if 'country' in dreisiebeneins.keys():
                country = dreisiebeneins['country']
            if 'cities' in dreisiebeneins.keys():
                city = dreisiebeneins['cities'][0]
                if (regexpspaceordash.search(city)):
                     cityparts = regexpspaceordash.split(city)
                     citypartvariations = {}
                     citypartnormed = {}
                     for citypart in cityparts:
                 	    citypartvariations[citypart] = [ citypart ]
                 	    citypartnormed[citypart] = citypart 
                 	    for particle in particles:
                 		    if (citypart in particle):
                 			    citypartvariations[citypart] = particle
                 			    citypartnormed[citypart] = particle[1]
                     normedcity = ''.join([ citypartnormed[citypart]+'-' for citypart in cityparts])[0:-1]
                     for variation in crossloop([citypartvariations[citypart] for  citypart in cityparts]):
                                version1 = ''.join(part+' ' for part in variation)[0:-1]
                                version2 = ''.join(part+'-' for part in variation)[0:-1]
                                if not version1 == normedcity:
                                    normcities[version1] = normedcity.title()
                                if not version2 == normedcity:
                                    normcities[version2] = normedcity.title()
            if 'postal_address' in dreisiebeneins.keys():
                address = ', '.join(dreisiebeneins['postal_address'])
                if 'postal_code' in dreisiebeneins.keys():
                    plz = dreisiebeneins['postal_code']
                # don't write country in capital letters!
                if regexpaddress.search(address):
                    tail = regexpaddress.sub(r'\1\2\3',address)
                    address = re.sub(tail,tail.title(),address)
                elif regexpcc.search(address):
                    tail = regexpcc.sub(r'\1',address)                
                    if len(tail) > 3:
                        address = re.sub(tail,tail.title(),address)                    
            #print '  CC=',cc
            #print '  CITY=',city
            #print '   ADDRESS=',address
            #print '   COUNTRY=',country
            afflineappendix = ";   "+icn+";   "+dlu+";   "+cc+";   "+city+core+grid
            if ((len(address)>3) or country + city != '') and not (icn == ''):
                if organization == '':
                    if department == '':
                        afflines = [ address ]
                    else:
                        afflines = [ department + ', ' + address ]
                else:
                    if department == '':
                        afflines = [ organization + ', ' + address ]
                    else:
                        afflines = [ department + ', ' + organization + ', ' + address,
                                     organization + ', ' + department + ', ' + address]
                for affline in afflines:
                    #adfioldwrite(affline, afflineappendix)
                    affapplines.append((affline, afflineappendix))
                    if country != '' and not re.search(country, affline, flags=re.IGNORECASE):
                        #adfioldwrite(affline + ', ' + country, afflineappendix)
                        affapplines.append((affline + ', ' + country, afflineappendix))
                        if city != '' and not re.search(city, affline, flags=re.IGNORECASE):
                            #adfioldwrite(affline + ', ' + plz+city + ', ' + country, afflineappendix)
                            affapplines.append((affline + ', ' + plz+' '+city + ', ' + country, afflineappendix))
                    if city != '' and not re.search(city, affline, flags=re.IGNORECASE):
                        #adfioldwrite(affline + ', ' + plz+city, afflineappendix)
                        affapplines.append((affline + ', ' + plz+' '+city, afflineappendix))
            else:
                print '???', address, icn
    if (regexpunlisted.search(icn)):
        address = re.sub(' ', '-', address)
        countriescc[address] = cc
    old = False
    if 'inactive' in institute.keys() and institute['inactive']:
        old = True
        print '%s is DEAD' % (icn)
    if old:
        if not icn in oldicns:
            oldicns.append(icn)
    else:
        if 'successor' in get_fieldvalues(recid, ['related_records', 'record', 'relation_freetext']):
            old = True
            oldicns.append(icn)
            print '%s has a successor' % (icn)
    #if  not old and 'a' in relations:
    #    for entry in institute['510']:
    #        for subentry in entry[0]:
    #            if subentry[0] == 'a':
    #                othericn = subentry[1]
    #            elif subentry[0] == 'w':
    #                relation = subentry[1]
    #        if relation == 'a':
    #            if not othericn in oldicns:
    #                oldicns.append(othericn)
    #            print '%s has a predecessor: %s' % (icn, othericn)
    newaffdict[icn] = affapplines

    print affapplines


#adfi = open(knowledgebasepath+'/aff-dlu-from-labs.afb', 'w')
adfi = codecs.open(knowledgebasepath+'/aff-dlu-from-labs.afb', encoding='utf-8', mode='w')
adfi.write('# affiliation -> dlu database from INST database of LABS (without old institutes)\n')
#adfiold = open(knowledgebasepath+'/aff-dlu-from-labs-old.afb', 'w')
adfiold = codecs.open(knowledgebasepath+'/aff-dlu-from-labs-old.afb', encoding='utf-8', mode='w')
adfiold.write('# affiliation -> dlu database from INST database of LABS (with old institutes)\n')
for icn in  newaffdict.keys():
    for (affline, afflineappendix) in newaffdict[icn]:
        adfioldwrite(affline, afflineappendix)
        if not icn in oldicns:
            adfiwrite(affline, afflineappendix)

#workaround: Serbia and not Montenegro
adfiold.write('Montenegro;   Unlisted, ME;   unlisted ME;   ME;   ;   ;   ;\n')
adfi.write('Montenegro;   Unlisted, ME;   unlisted ME;   ME;   ;   ;   ;\n')


adfi.close()
adfiold.close()



ouf = open(knowledgebasepath+'/countriescc.pickle', 'w')
cPickle.dump(countriescc,ouf,2)
ouf.close()
ouf = open(knowledgebasepath+'/normcities.pickle', 'w')
cPickle.dump(normcities,ouf,2)
ouf.close()

