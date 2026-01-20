import pandas as pd
import numpy as np
from cleverminer import cleverminer
import io
import sys

# =============================================================================
# 1. NAČTENÍ A PŘÍPRAVA DAT
# =============================================================================
print("Načítám data...")
# Načtení sloučeného souboru
df = pd.read_csv('merged_data.csv', delimiter=',', engine='python', on_bad_lines='skip')

# Převedení data a seřazení (nutné pro správný výběr posledního záznamu)
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by=['fips', 'date'])

# Odstranění duplicit - necháme si jen "stav tachometru" na konci roku
df_final = df.drop_duplicates(subset=['fips'], keep='last').copy()
print(f"Finální počet unikátních okresů: {len(df_final)}")

# =============================================================================
# 2. FEATURE ENGINEERING (Vytvoření kategorií)
# =============================================================================

# A) dopočítání procent ras (pokud v CSV náhodou chybí nebo jsou jinak nazvané)
# Používáme sloupce z Population datasetu
if 'pct_black' not in df_final.columns:
    # Pojistka: výpočet, pokud chybí
    # Zkontrolujeme, zda máme zdrojové sloupce, jinak předpokládáme, že už tam jsou
    if 'black_alone_male' in df_final.columns:
        df_final['pct_black'] = (df_final['black_alone_male'] + df_final['black_alone_female']) / df_final['total_population']
        df_final['pct_white'] = (df_final['white_alone_male'] + df_final['white_alone_female']) / df_final['total_population']

# B) Vytvoření "Race_Context" (Rasový kontext okresu)
# Rozdělíme okresy do skupin podle demografie
def categorize_race(row):
    # Pokud je podíl černošské populace vyšší než 20% (významná menšina/většina)
    # Pozn: Průměr v USA je cca 13%, takže 20% je silný indikátor
    if row['pct_black'] > 0.20:
        return 'Black_Significant'
    # Pokud je podíl bílé populace extrémně vysoký (nad 85%)
    elif row['pct_white'] > 0.85:
        return 'White_Dominant'
    else:
        return 'Mixed/Other'

df_final['Race_Context'] = df_final.apply(categorize_race, axis=1)

# C) Vytvoření CFR Level (Úmrtnost) - rozdělíme na High/Low podle mediánu
# Poznámka: Pro SD4ft je lepší mít 2 kategorie (High vs zbytek), lépe se porovnávají rozdíly
median_cfr = df_final['case_fatality_rate_pct'].median()
df_final['CFR_level'] = df_final['case_fatality_rate_pct'].apply(
    lambda x: 'High CFR' if x > median_cfr else 'Low CFR'
)

# D) Kontrola/Vytvoření kategorie chudoby
# Pokud už máš 'poverty_category' z SQL, použijeme ji. Pokud ne, vytvoříme ji.
if 'poverty_category' not in df_final.columns or df_final['poverty_category'].isnull().all():
    # Vytvoření kategorií (kvartily nebo fixní hranice)
    df_final['poverty_category'] = pd.cut(
        df_final['poverty_percent_all_ages'], 
        bins=[-1, 10, 15, 20, 100], 
        labels=['Low', 'Medium', 'High', 'Very High']
    ).astype(str)

# =============================================================================
# 3. FILTROVÁNÍ PRO MINING
# =============================================================================
# Vybereme jen potřebné sloupce a vyhodíme Unknown
cols_needed = ['poverty_category', 'income_category', 'CFR_level', 'Race_Context']
# Ověříme, že sloupce existují
cols_needed = [c for c in cols_needed if c in df_final.columns]

df_mining = df_final[cols_needed].copy()
# Odstraníme řádky s chybějícími daty
df_mining = df_mining.replace('Unknown', np.nan).dropna()

print(f"Data připravena pro SD4ft: {len(df_mining)} řádků")
print("\nRozložení skupin Race_Context:")
print(df_mining['Race_Context'].value_counts())

# =============================================================================
# 4. SPUŠTĚNÍ SD4ft-MINER
# =============================================================================
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

# =============================================================================
# 5. VÝSTUP
# =============================================================================
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

# Seřadíme pravidla, aby ta nejzajímavější byla nahoře (podle Ratiopim)
# Pozn: Pokud knihovna nepodporuje přímé řazení, vypíšeme tak, jak jsou
if hasattr(clm, 'rulelist'):
    # Zkusíme seřadit, pokud to jde
    try:
        clm.rulelist.sort(key=lambda r: r.q_values.get('Ratiopim', 0), reverse=True)
    except:
        pass # Necháme původní pořadí
    
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