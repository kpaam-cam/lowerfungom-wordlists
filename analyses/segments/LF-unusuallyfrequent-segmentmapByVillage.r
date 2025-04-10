library(lingtypology)
library(mapview)
library(dplyr) # for magrittr function
source("/Users/jcgood/gitrepos/tls/scripts/labelMaps.R") # Custom function based on lingtypology for label maps

# Map of segments with highest zscore for LF by village 
langs = c("Mungbam", "Ajumbu", "Mungbam", "Buu", "Fang (Cameroon)", "Koshin", "Kung", "Naki", "Mungbam", "Mundabli-Mufu", "Mundabli-Mufu", "Mungbam", "Mungbam")
labels = c("o",
 "ɲ",
 "bʷ",
 "oː",
 "l",
 "⁵¹",
 "ʔ",
 "d",
 "i",
 "ŋ",
 "³",
 "mʷ",
 "kʷ")
feats = c(27, 25, 8, 16, 29, 26, 22, 27, 34, 36, 36, 5, 12)
popups = c("Abar<br/>27",
 "Ajumbu<br/>25",
 "Biya<br/>8",
 "Buu<br/>16",
 "Fang<br/>29",
 "Koshin<br/>26",
 "Kung<br/>22",
 "Mashi<br/>27",
 "Missong<br/>34",
 "Mumfu<br/>36",
 "Mundabli<br/>36",
 "Munken<br/>5",
 "Ngun<br/>12")
lats = c(6.577583, 6.5391, 6.592167, 6.56465, 6.549667, 6.58815, 6.561033, 6.600783, 6.59745, 6.612433, 6.606933, 6.5953, 6.5814)
longs = c(10.236533000000001, 10.237567, 10.204533000000001, 10.254150000000001, 10.278017, 10.280317, 10.219383, 10.264667000000001, 10.24615, 10.256167000000001, 10.272300000000001, 10.222467, 10.211583000000001)
map = map.feature.label(languages = langs, label = labels, features = feats, popup = popups, latitude = lats, longitude = longs, label.hide = FALSE, color="magma")
