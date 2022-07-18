import pandas
import re

latlongs = pandas.read_csv("../raw/" + "LFLatLongs" + ".tsv", sep="\t") 
entries = latlongs.to_dict(orient='records')

# First convert to decimal
output = "Village\tLatLong\tLatitude\tLongitude\n"
LatLongIndex = { }
for entry in entries:

	Village = entry["Village"]
	LatLong = entry["LatLong"]
	
	LatLongMatch = re.search("N(\d+)\s([\d.]+)\sE(\d+)\s([\d.]+)", LatLong)
	
	LatDegs = float(LatLongMatch[1])
	LatMins = float(LatLongMatch[2])
	LongDegs = float(LatLongMatch[3])
	LongMins = float(LatLongMatch[4])
	
	LatMinDec =  LatMins/60
	LongMinDec = LongMins/60
	
	LatDec = round(LatDegs+LatMinDec, 4)
	LongDec = round(LongDegs+LongMinDec, 4)
	
	s = "\t"
	newLine = s.join([str(Village),str(LatLong),str(LatDec),str(LongDec)]) + "\n"
	
	LatLongIndex[Village] = [LatDec, LongDec]
	
	output = output + newLine

outputFile = open("../raw/" + "LFLatLongs" + ".tsv", "w")
outputFile.write(output)


# Now do some updating to etc/languages.tsv
languageTable = pandas.read_csv("../etc/" + "languages" + ".tsv", sep="\t") 
languoids = languageTable.to_dict(orient='records')

langOutput = "ID\tName\tGlottocode\tVariety\tLatitude\tLongitude\n"
for languoid in languoids:
	
	ID = languoid["ID"]
	Name = languoid["Name"]
	Glottocode = languoid["Glottocode"]
	
	# Get village name from Name variable
	VarietyMatch = re.search(".*-(.*)-.*", Name)
	Variety = VarietyMatch[1]
	if Variety == "Mumfu": Variety = "Mufu"
	
	Lat, Long = LatLongIndex[Variety]
	
	s = "\t"
	updatedLine = s.join([str(ID),str(Name),str(Glottocode),str(Variety),str(Lat),str(Long)]) + "\n"
	
	langOutput = langOutput + updatedLine

outputFile = open("../etc/" + "languages" + ".tsv", "w")
outputFile.write(langOutput)
