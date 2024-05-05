# Step 1 to prepare new wordlists for analysis
# To be used with prepareParallelListsForCLDF-wNewWordlists.py
# Maybe combine these?

import pandas
import math


# hack to work with legacy process
wordlistFile = "Grollemund-cognates.csv"


wordlists = pandas.read_csv("../raw/" + wordlistFile, header=0)
wordlists = wordlists.fillna('')

headernames = wordlists.columns.values.tolist()

# get rid of non-data headers
concepts = [ ]
for header in headernames:
	if header == "Language":
		pass
	elif header == "Sources":
		pass
	elif "Unnamed" in header:
		pass
	else:
		concepts.append(header)

FormsByLanguage = { }
for index, entry in wordlists.iterrows():

	language = entry["Language"]
	language = language.replace("*", "STAR_")
	
	# run through the row
	forms = { }
	for concept in concepts:
		form = entry[concept]
		# data cleaning
		form = form.replace("\n", " ")
		form = form.replace("\t", " ")
		forms[concept] = form
	FormsByLanguage[language] = forms


for language in FormsByLanguage.keys():
	formCount = 0
	forms = FormsByLanguage[language]
	for concept in concepts:
		form = forms[concept]
		if form != "?":
			formCount = formCount + 1
	print(language + "\t" + str(formCount))

