# afftranslator

afftranslator translates an affiliation given as a plain string into the 
standardized ICN (or DLU) of the SPIRES/INSPIRE database.

The code is written by florian.schwennsen@desy.de. It is ugly and slow (even 
though I improved it befor putting it on git) but it works. Every serious 
developer should have a darf bag within reach befor looking at the code.

In aff-dlu-from-inspire.py and afftranslator2.py the path where to find the 
pickle-files are explictly defined. You need to change it probably.
If you want the knowledge base be up to date you have to run 
aff-dlu-from-inspire.py and generateknowledgebase.py regularily.
Please note that generateknowledgebase.py runs for several hours.


The following files belong to the package

 - 'aff-dlu-from-inspire.afb' contains the list of affiliations from the INST 
   database.

 - 'aff-dlu-from-inspire-old.afb' contains the list of affiliations from the INST 
   database including dead institutes and institutes with a successor. *)

 - 'aff-dlu-from-inspire.py'  generates the file aff-dlu-from-inspire.afb.

 - 'aff-translator.pickle' contains the main informations with different
   writings of the affilitations, normalizations of these writings, acronyms 
   etc.  including dead institutes and institutes with a successor. *)

 - 'aff-translator-old.pickle' contains the main informations with different
   writings of the affilitations, normalizations of these writings, acronyms 
   etc.

 - 'afftranslator2.py' is the main program from which usually just the
   function 'bestmatch' is needed. There are some parameters which one can 
   play with but it might get worse globally if you try to improve the 
   matching of one specific affiliation.
   
 - 'countriescc.pickle' contains the normalization of country names.

 - 'footnotes.afb' contains text which sometimes by mistake ends up in
   the affiliation field and which should be removed.

 - 'frequentwords' contains a list of words that often appear in affiliation 
   strings and that can be given a lower weight in the matching process.

 - 'generateknowledgebase.py' generates the pickle-files.

 - 'normcities.pickle' contains the normalization of city names.

 - 'sj.afb' contains the knowledge of affiliations that already have been
   mapped to ICNs. It contains 80.000 lines - some of them probably wrong
   (even though I checked them). Adding corrected lines (where afftranslator 
   failed in the first place) improves later results.

 - 'test.py' is a little example how to use afftranslator.




*) these *-old.* files are a work around as I just now implemented the
   possibility to use
       bestmatch('bla bla', 'ICN', old=True)
   for old stuff where expired institutes might appear. It is not a proper
   implementation where you could set the flag differently in subsequent calls
   of the function. The pickle-file is loaded once and at this first load you 
   have to decide.
   This is different to the flag 'onlycore' which I implemented from the very
   beginning and which reduces the search to core institutes.
