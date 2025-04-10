# Find the most salient form in the wordlist: That is, the one that is most distinctive for a given variety, code generated via copilot

import pandas as pd

forms_df = pd.read_csv('../cldf/forms.csv')

salience_scores_df = pd.read_csv('../analyses/segments/allSalienceScores-Grollemund.tsv', sep='\t')

# Create a dictionary for quick lookup of salience scores
salience_dict = { }
for index, row in salience_scores_df.iterrows():
    key = (row['Doculect'], row['Segment']) # key is a tuple
    salience_dict[key] = row['SalienceScore']

# Function to calculate overall salience score for a list of segments
def calculate_overall_salience(segments, language_id):
    total_salience = 0
    count = 0
    for segment in segments:
        key = (language_id, segment)
        if key in salience_dict:
            total_salience += salience_dict[key]
            count += 1
    if count > 0:
        return round(total_salience / count)
    return 0

# Process each form to calculate overall salience score
results = [ ]
for index, row in forms_df.iterrows():
    language_id = row['Language_ID']
    parameter_id = row['Parameter_ID']
    segments = row['Segments'].split()
    form = "".join(segments)
    overall_salience = calculate_overall_salience(segments, language_id)
    results.append([language_id, parameter_id, form, " ".join(segments), overall_salience])

# Create a DataFrame from the results
results_df = pd.DataFrame(results, columns=['Doculect', 'Gloss', 'Form' ,'Segments', 'SalienceScore'])

# Group by Language_ID and sort by SalienceScore within each group
sorted_results_df = results_df.sort_values(by=['Doculect', 'SalienceScore'], ascending=[True, False])

# Get the highest salience score for each group
highest_salience_df = sorted_results_df.groupby('Doculect').first().reset_index()

# Output the highest salience scores to a new file
highest_salience_df.to_csv('../analyses/segments/highestSalienceForms-Grollemund.tsv', index=False, sep="\t")


