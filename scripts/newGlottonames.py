# Minor script to help with glottoname cleanup for lingtypology mapping
# This didn't work since the pyglottolog API didn't seem to work like I'd expect
# Gave up...
import pyglottolog
import pandas as pd

# Mapping to regular language names is in a difference CLDF file
languageFile = "../../../gitrepos/grollemundbantu/cldf/languages.csv"
languageDF = pd.read_csv(languageFile)

for index, row in languageDF.iterrows():
    glottocode = row["Glottocode"]
    glottolog = pyglottolog.Glottolog(glottocode)
    print(glottolog)
	