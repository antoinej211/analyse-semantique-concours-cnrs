import os
import glob
import re
import pandas as pd

def parse_document(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    data = {
        'competition_number': None,
        'post_number': None,
        'job_type': None,
        'city': None,
        'research_institute': None,
        'domain': None,
        'job_category': None,
        'remote_work': 0,
        'education_level': None,
        'english_proficiency': 'NaN',
        'has_r': 0,
        'has_python': 0,
        'has_ml': 0,
        'it_skills': 0,
        'stat_methods': 0,
        'has_formation': 0,
        'has_encadrement': 0
    }

    comp_num_match = re.search(r"Concours N°\s*(\d+)", text)
    if comp_num_match:
        data['competition_number'] = comp_num_match.group(1)

    post_num_match = re.search(r"Nbre de postes\s*:\s*(\d+)", text)
    if post_num_match:
        data['post_number'] = post_num_match.group(1)

    if re.search(r"Ingénieur de recherche", text, re.IGNORECASE):
        data['job_type'] = 'IR'
    elif re.search(r"Ingénieur d'études", text, re.IGNORECASE):
        data['job_type'] = 'IE'

    affectation_match = re.search(r"Affectation\s*:\s*(.*?),\s*(.*)", text)
    if affectation_match:
        data['research_institute'] = affectation_match.group(1).strip()

        raw_city = affectation_match.group(2).strip().lower()

        clean_city = raw_city.replace('"', '').replace("'", "")

        clean_city = re.sub(r'\d+', '', clean_city)

        clean_city = clean_city.replace('cedex', '')

        clean_city = re.sub(r'\s+[a-z]\b', '', clean_city)

        data['city'] = clean_city.strip()

    domain_match = re.search(r"^([A-Z])\s*:\s*(.*)", text, re.MULTILINE)
    if domain_match:
        data['job_category'] = domain_match.group(1).strip()
        data['domain'] = domain_match.group(2).strip()

    text_lower = text.lower()

    if re.search(r"télétravail|telework|remote", text_lower):
        data['remote_work'] = 1

    if re.search(r"doctorat|phd|bac\s*\+\s*8", text_lower):
        data['education_level'] = 'D'
    elif re.search(r"master|ingénieur|bac\s*\+\s*5", text_lower):
        data['education_level'] = 'M'
    elif re.search(r"licence|bac\s*\+\s*3", text_lower):
        data['education_level'] = 'L'

    english_match = re.search(r"anglais.*?(a1|a2|b1|b2|c1|c2)", text_lower)
    if english_match:
        data['english_proficiency'] = english_match.group(1).upper()
    elif re.search(r"anglais courant|fluent english", text_lower):
        data['english_proficiency'] = 'C1'

    if re.search(r'\br\b', text_lower):
         data['has_r'] = 1
    if 'python' in text_lower:
         data['has_python'] = 1
    if any(kw in text_lower for kw in ['machine learning', 'deep learning', 'ia', 'intelligence artificielle']):
         data['has_ml'] = 1
    if any(kw in text_lower for kw in ['bio-informatique', 'informatique', 'développement', 'pipeline']):
         data['it_skills'] = 1
    if any(kw in text_lower for kw in ['statistique', 'analyse de données']):
         data['stat_methods'] = 1
    if any(kw in text_lower for kw in ['formation', 'enseigner']):
         data['has_formation'] = 1
    if any(kw in text_lower for kw in ['encadrement', 'superviser', 'manager', 'équipe']):
         data['has_encadrement'] = 1

    return data


folder_path = 'data_extract/data'

file_pattern = os.path.join(folder_path, '*.txt')
text_files = glob.glob(file_pattern)

all_parsed_data = []

print(f"Found {len(text_files)} files. Starting extraction...")

for file_path in text_files:
    try:

        file_data = parse_document(file_path)

        file_data['source_file'] = os.path.basename(file_path)

        all_parsed_data.append(file_data)

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

df = pd.DataFrame(all_parsed_data)

output_csv_name = 'concours_dataset_complete.csv'
df.to_csv(output_csv_name, index=False, encoding='utf-8')

print(f"Extraction complete! Saved {len(df)} rows to {output_csv_name}.")