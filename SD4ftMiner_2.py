import pandas as pd
import numpy as np
from cleverminer import cleverminer
import io
import sys


print("Načítám data...")

df = pd.read_csv('merged_data.csv', delimiter=',', engine='python', on_bad_lines='skip')


if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by=['fips', 'date'])

df_final = df.drop_duplicates(subset=['fips'], keep='last').copy()
print(f"Finální počet unikátních okresů: {len(df_final)}")

if 'pct_black' not in df_final.columns:

    if 'black_alone_male' in df_final.columns:
        df_final['pct_black'] = (df_final['black_alone_male'] + df_final['black_alone_female']) / df_final['total_population']
        df_final['pct_white'] = (df_final['white_alone_male'] + df_final['white_alone_female']) / df_final['total_population']

def categorize_race(row):
  
    if row['pct_black'] > 0.20:
        return 'Black_Significant'

    elif row['pct_white'] > 0.85:
        return 'White_Dominant'
    else:
        return 'Mixed/Other'

df_final['Race_Context'] = df_final.apply(categorize_race, axis=1)

median_cfr = df_final['case_fatality_rate_pct'].median()
df_final['CFR_level'] = df_final['case_fatality_rate_pct'].apply(
    lambda x: 'High CFR' if x > median_cfr else 'Low CFR'
)


if 'poverty_category' not in df_final.columns or df_final['poverty_category'].isnull().all():
    # Vytvoření kategorií (kvartily nebo fixní hranice)
    df_final['poverty_category'] = pd.cut(
        df_final['poverty_percent_all_ages'], 
        bins=[-1, 10, 15, 20, 100], 
        labels=['Low', 'Medium', 'High', 'Very High']
    ).astype(str)


cols_needed = ['poverty_category', 'income_category', 'CFR_level', 'Race_Context']

cols_needed = [c for c in cols_needed if c in df_final.columns]

df_mining = df_final[cols_needed].copy()

df_mining = df_mining.replace('Unknown', np.nan).dropna()

print(f"Data připravena pro SD4ft: {len(df_mining)} řádků")
print("\nRozložení skupin Race_Context:")
print(df_mining['Race_Context'].value_counts())

print("\n=== SPUŠTĚNÍ SD4FT-MINER ===")
print("Hledáme: Zda chudoba (Antecedent) vede k vysoké úmrtnosti (Succedent)")
print("Porovnáváme: Okresy s černošskou populací (FRST) vs. Bílé okresy (SCND)")

clm = cleverminer(
    df=df_mining,
    proc='SD4ftMiner',
    quantifiers={
        'Base1': 50,    # Alespoň 50 okresů ve skupině 1 (Black)
        'Base2': 100,   # Alespoň 100 okresů ve skupině 2 (White)
        'Ratiopim': 1.2 # Rozdíl v pravděpodobnosti musí být alespoň 20% (1.2 násobek)
    },
    ante={
        'attributes': [
            {'name': 'poverty_category', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
            {'name': 'income_category', 'type': 'subset', 'minlen': 1, 'maxlen': 1}
        ], 
        'minlen': 1, 
        'maxlen': 1, 
        'type': 'con'
    },
    succ={
        'attributes': [
            {'name': 'CFR_level', 'type': 'subset', 'minlen': 1, 'maxlen': 1}
        ], 
        'minlen': 1, 
        'maxlen': 1, 
        'type': 'con'
    },
    frst={ # První skupina: Black Significant
        'attributes': [
            {'name': 'Race_Context', 'type': 'one', 'value': 'Black_Significant'}
        ], 
        'minlen': 1, 
        'maxlen': 1, 
        'type': 'con'
    },
    scnd={ # Druhá skupina: White Dominant
        'attributes': [
            {'name': 'Race_Context', 'type': 'one', 'value': 'White_Dominant'}
        ], 
        'minlen': 1, 
        'maxlen': 1, 
        'type': 'con'
    }
)


output = io.StringIO()
sys.stdout = output

print("=== SD4FT-MINER ANALYSIS REPORT ===\n")
print("Task: Race Disparity Analysis (Poverty -> High Mortality)\n")
print("Group 1 (FRST): Black Significant (>20% population)")
print("Group 2 (SCND): White Dominant (>85% population)\n")

clm.print_summary()
print("\n---------------------------------------------------")
print("NALEZENÁ PRAVIDLA (Seřazeno podle síly rozdílu):")
print("---------------------------------------------------\n")


if hasattr(clm, 'rulelist'):

    try:
        clm.rulelist.sort(key=lambda r: r.q_values.get('Ratiopim', 0), reverse=True)
    except:
        pass 
    
    clm.print_rulelist()
    
    for i in range(1, len(clm.rulelist) + 1):
        print(f"\n=== Rule {i} ===")
        clm.print_rule(i)
else:
    print("Žádná pravidla nebyla nalezena (zkontrolujte limity Base/Ratiopim).")

sys.stdout = sys.__stdout__

# Uložení do souboru
filename = "SD4ftMiner_2.txt"
with open(filename, "w", encoding="utf-8") as f:
    f.write(output.getvalue())

print(output.getvalue())
print(f"\nVýstup byl úspěšně uložen do souboru: {filename}")