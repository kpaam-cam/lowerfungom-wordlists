from pysem.glosses import to_concepticon
import pandas
import os

conceptList = pandas.read_csv("../raw/" + "ConceptList.csv") 
concepts = conceptList.to_dict(orient="records")

for key, matches in to_concepticon(concepts, language="en", gloss_ref="Concept").items():
	print(key, matches)