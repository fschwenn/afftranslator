#!/usr/bin/python
# run on inspire.desy.de
#

import re
import sys
import os
import unicodedata
import cPickle
#from unidecode import unidecode
from invenio.search_engine import search_pattern
from invenio.search_engine import get_most_popular_field_values
from invenio.search_engine import get_fieldvalues
from invenio.search_engine import get_record
from invenio.search_engine import get_collection_reclist
from sets import Set

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
        unicode_text= unicodedata.normalize('NFD', text.decode('utf-8'))
        return filter(not_combining, unicode_text).encode('ASCII','ignore')

def adfiwrite(affline, afflineappendix):
    affline = regexpserbia.sub('Serbia', affline) + afflineappendix
    afflinestripped = strip_accents(affline)
    adfi.write(affline)
    #print affline
    if not afflinestripped == affline:
        adfi.write(afflinestripped) 
    return
def adfioldwrite(affline, afflineappendix):
    affline = regexpserbia.sub('Serbia', affline) + afflineappendix
    afflinestripped = strip_accents(affline)
    adfiold.write(affline)
    #print affline
    if not afflinestripped == affline:
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
    


adfiold = open(knowledgebasepath+'/aff-dlu-from-inspire-old.afb', 'w')
adfiold.write('# affiliation -> dlu database from INST database of INSPIRE (with old institutes)\n')



countriescc = {}
normcities = {}
#informations from INSPIRE
institutes = search_pattern(p="980__a:INSTITUTION  not 980:DELETED not 980:DEAD not 001:910325 not 001:910584")
#institutes = search_pattern(p="980__a:INSTITUTION  not 980:DELETED not 980:DEAD not 001:910325 not 001:910584 and not 510__w:b")
print len(institutes),'institutes found'


i = 0
for recid in institutes:
    i += 1
    if i % 500 == 0: 
        print ' --- %i/%i ---' % (i, len(institutes))
    institute = get_record(recid)
    if not institute.has_key('110'):
        print '!', recid
        continue
    else:
        affapplines = []
        #identifiers
        icn =  get_most_popular_field_values(recid, '110__u')
        if len(icn) > 0: icn = icn[0][0]
        else: icn = ''
        if regexpunlistedus.search(icn):
            continue
        newicn =  get_most_popular_field_values(recid, '110__t')
        if len(newicn) > 0: newicn = newicn[0][0]
        else: newicn = ''
        organization =  get_most_popular_field_values(recid, '110__a')
        if len(organization) > 0: organization = organization[0][0]
        else: organization = ''
        department =  get_most_popular_field_values(recid, '110__b')
        if len(department) > 0: department = department[0][0]
        else: department = ''
        dlu = ''
        #coreness
        core = ';   ;\n'
        if institute.has_key('980'):
            for entry in institute['980']:
                if 'CORE' in entry[0][0]:
                    core = ';   CORE;\n'
            
        #DLU
        if institute.has_key('410'):
            for line in institute['410']:
                if len(line[0])>1:
                    if line[0][1] == ('9', 'DESY'):
                        dlu = line[0][0][1]
                    elif line[0][0] == ('9', 'DESY'):
                        dlu = line[0][1][1]
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
        #address
        if not institute.has_key('371'):
            print '!!!',recid,'keine Adresse !!!'
            sys.exit()
        for dreisiebeneins in institute['371']:
            cc = ''
            country = ''
            city = ''
            address = ''
            plz = ''
            for entry in dreisiebeneins[0]:
                if entry[0] == 'g':
                    cc = entry[1]
                    #if len(cc) > 0: cc = cc[0][0]
                elif entry[0] == 'b':
                    city = entry[1]
                    #if len(city) > 0: city = city[0][0].title()
                    if (regexpstartingspace.search(city)) or (regexptrailingspace.search(city)):
                        print recid,'city = "'+city+'"'
                    if (regexpspaceordash.search(city)):
                    #normcities[city] = re.sub(' ','-',city)
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
                elif entry[0] == 'a':
                    address += entry[1]+', '
                elif entry[0] == 'd': 
                    country = entry[1]
                elif entry[0] == 'e':
                    plz = entry[1] + ' '
            address = regexptrailingcomma.sub('', address)
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
            afflineappendix = ";   "+icn+";   "+dlu+";   "+cc+";   "+city+core
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
                #workaround: Serbia and not Montenegro
                for affline in afflines:
                    adfioldwrite(affline, afflineappendix)
                    affapplines.append((affline, afflineappendix))
                    if country != '' and not re.search(country, affline, flags=re.IGNORECASE):
                        adfioldwrite(affline + ', ' + country, afflineappendix)
                        affapplines.append((affline + ', ' + country, afflineappendix))
                        if city != '' and not re.search(city, affline, flags=re.IGNORECASE):
                            adfioldwrite(affline + ', ' + plz+city + ', ' + country, afflineappendix)
                            affapplines.append((affline + ', ' + plz+city + ', ' + country, afflineappendix))
                    if city != '' and not re.search(city, affline, flags=re.IGNORECASE):
                        adfioldwrite(affline + ', ' + plz+city, afflineappendix)
                        affapplines.append((affline + ', ' + plz+city, afflineappendix))
            else:
                print '???', address, icn
        if (regexpunlisted.search(icn)):
	    address = re.sub(' ', '-', address)
	    countriescc[address] = cc
        old = False
        for dead in get_fieldvalues(recid, '980__a'):
            if dead == 'DEAD':
                old = True
                print '%s is DEAD' % (icn)
        for dead in get_fieldvalues(recid, '980__b'):
            if dead == 'DEAD':
                old = True
                print '%s is DEAD' % (icn)
        if not old:
            relations = get_fieldvalues(recid, '510__w')
            for history in relations:
                if history == 'b': 
                    old = True
                    print '%s has a successor' % (icn)
        if  not old and 'a' in relations:
            for entry in institute['510']:
                for subentry in entry[0]:
                    if subentry[0] == 'a':
                        othericn = subentry[1]
                    elif subentry[0] == 'w':
                        relation = subentry[1]
                if relation == 'a':
                    oldicns.append(othericn)
                    print '%s has a predecessor: %s' % (icn, othericn)
        if not old:
            newaffdict[icn] = affapplines


#workaround: Serbia and not Montenegro
adfiold.write('Montenegro;   Unlisted, ME;   unlisted ME;   ME;   ;\n')
adfiold.close()

adfi = open(knowledgebasepath+'/aff-dlu-from-inspire.afb', 'w')
adfi.write('# affiliation -> dlu database from INST database of INSPIRE (without old institutes)\n')
for icn in  newaffdict.keys():
    if not icn in oldicns:
        for (affline, afflineappendix) in newaffdict[icn]:
            adfiwrite(affline, afflineappendix)
adfi.close()



ouf = open(knowledgebasepath+'/countriescc.pickle', 'w')
cPickle.dump(countriescc,ouf,2)
ouf.close()
ouf = open(knowledgebasepath+'/normcities.pickle', 'w')
cPickle.dump(normcities,ouf,2)
ouf.close()

