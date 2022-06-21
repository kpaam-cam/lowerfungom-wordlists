import pandas
import os

# Helps clean up an issue with diverging IDs and older and newer lists; should be a throwaway script

oldConceptFile = pandas.read_csv("../raw/" + "OldMasterConceptList" + ".csv" ) 
newConceptFile = pandas.read_csv("../raw/" + "CurrentConceptList" + ".csv" ) 

oldConceptEntries = oldConceptFile.to_dict(orient='records')
newConceptEntries = newConceptFile.to_dict(orient='records')

outputFile = open("../raw/" "OldNewMapping.tsv", "w")
header = "OldConceptID\tNewConceptID\tOldConcept"
outputFile.write(header + "\n")

oldConcepts = { }
for oldConcept in oldConceptEntries:

	oldConceptID = oldConcept["ID"]
	oldConceptName = oldConcept["name"]
	oldConceptName = oldConceptName.strip()

	if oldConceptName in oldConcepts.keys():
		print("Old duplicate name: " + oldConceptName)
		pass
	else: oldConcepts[oldConceptName] = oldConceptID


newConcepts = { }
for newConcept in newConceptEntries:

	newConceptID = newConcept["ID"]
	newConceptName = newConcept["name"]
	newConceptName = newConceptName.strip()


	if newConceptName in newConcepts.keys():
		#print("New duplicate name: " + newConceptName)
		pass
	else: newConcepts[newConceptName] = newConceptID

for oldConcept in oldConcepts:

	oldConceptID = oldConcepts[oldConcept]
	
	try: newConceptID = newConcepts[oldConcept]
	except:
		newConceptID = "N/A"
	
	s = "\t"
	newRow = s.join([str(oldConceptID), str(newConceptID), oldConcept])
	
	outputFile.write(newRow + "\n")
	print(newRow)