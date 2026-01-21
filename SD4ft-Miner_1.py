import pandas as pd
from cleverminer import cleverminer
import io
import sys

# 1. Načtení a příprava dat (standardní postup)
df = pd.read_csv('merged_data.csv', delimiter=',', engine='python', on_bad_lines='skip')
df = df.sort_values(by=['fips', 'date'])
df_final = df.drop_duplicates(subset=['fips'], keep='last').copy()

# Filtrování prázdných hodnot
df_mining = df_final[df_final['case_fatality_rate_pct'].notna()].copy()

# Výpočet % žen (to musíme udělat)
df_mining['female_percent'] = (df_mining['total_female'] / df_mining['total_population']) * 100

print(f"Počet okresů: {len(df_mining)}")

# ==============================================================================
# 2. ZJEDNODUŠENÁ KATEGORIZACE (Bez ručních mediánů)
# ==============================================================================

# GENDER: Rozdělíme na 2 poloviny (q=2) -> "Nižší % žen" a "Vyšší % žen"
# Pandas si ten střed najde sám.
df_mining['gender_group'] = pd.qcut(
    df_mining['female_percent'], 
    q=2, 
    labels=['Lower Female %', 'Higher Female %']
)

# COUNTY SIZE: Rozdělíme na 2 poloviny -> "Small" a "Large"
df_mining['county_size'] = pd.qcut(
    df_mining['total_population'], 
    q=2, 
    labels=['Small', 'Large']
)

# CFR (Úmrtnost): Rozdělíme na 2 poloviny -> "Low CFR" a "High CFR"
df_mining['CFR_level'] = pd.qcut(
    df_mining['case_fatality_rate_pct'], 
    q=2, 
    labels=['Low CFR', 'High CFR']
)

# Převedeme na text (pro jistotu, aby to CleverMiner vzal)
df_mining['gender_group'] = df_mining['gender_group'].astype(str)
df_mining['county_size'] = df_mining['county_size'].astype(str)
df_mining['CFR_level'] = df_mining['CFR_level'].astype(str)

# Kontrola rozdělení (mělo by to být cca půl na půl)
print("\n=== Automatické rozdělení ===")
print(df_mining['gender_group'].value_counts())
print(df_mining['county_size'].value_counts())

# ==============================================================================
# 3. SD4ft-MINER
# ==============================================================================
# Cíl: Zjistit, jestli se pravidla liší v okresech s VÍCE ženami vs. MÉNĚ ženami.

df_sd4ft = df_mining[['gender_group', 'county_size', 'CFR_level']].copy()

clm = cleverminer(
    df=df_sd4ft,
    proc='SD4ftMiner',
    quantifiers={
        'Base1': 150,     # Minimálně 150 okresů v první skupině
        'Base2': 150,     # Minimálně 150 okresů ve druhé skupině
        'Ratiopim': 1.2   # Rozdíl v platnosti musí být alespoň 20 % (1.2x)
    },
    ante={
        'attributes': [
            {'name': 'county_size', 'type': 'subset', 'minlen': 1, 'maxlen': 1}
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
    # PRVNÍ MNOŽINA: Okresy s vyšším podílem žen
    frst={
        'attributes': [
            {'name': 'gender_group', 'type': 'one', 'value': 'Higher Female %'}
        ], 
        'minlen': 1, 
        'maxlen': 1,
        'type': 'con'
    },
    # DRUHÁ MNOŽINA: Okresy s nižším podílem žen
    scnd={
        'attributes': [
            {'name': 'gender_group', 'type': 'one', 'value': 'Lower Female %'}
        ], 
        'minlen': 1, 
        'maxlen': 1,
        'type': 'con'
    }
)

# 4. Výstup
output = io.StringIO()
sys.stdout = output

print("=== SD4FT-MINER: Vliv pohlaví na pravidla ===")
print("Srovnáváme okresy s vyšším podílem žen vs. nižším podílem žen.\n")

clm.print_summary()
print("\n")
clm.print_rulelist()

for i in range(1, len(clm.rulelist) + 1):
    print(f"\n=== Rule {i} ===")
    clm.print_rule(i)

sys.stdout = sys.__stdout__

with open("SD4ftMiner_1.txt", "w", encoding="utf-8") as f:
    f.write(output.getvalue())

print("\n" + output.getvalue())
print("\nVýstup uložen jako SD4ftMiner_1.txt")