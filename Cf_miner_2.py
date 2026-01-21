import pandas as pd
from cleverminer import cleverminer
import io
import sys

# 1. Načtení dat
df = pd.read_csv('merged_data.csv', delimiter=',', engine='python', on_bad_lines='skip')
df['date'] = pd.to_datetime(df['date'])

# 2. Definice vln (jen 2020)
# 1. vlna: březen - červen 2020
# 2. vlna: září - prosinec 2020
wave1_start = pd.to_datetime('2020-03-01')
wave1_end = pd.to_datetime('2020-06-30')
wave2_start = pd.to_datetime('2020-09-01')
wave2_end = pd.to_datetime('2020-12-31')

df_wave1 = df[(df['date'] >= wave1_start) & (df['date'] <= wave1_end)].copy()
df_wave2 = df[(df['date'] >= wave2_start) & (df['date'] <= wave2_end)].copy()

# 3. Poslední den každé vlny pro každý okres
df_wave1_final = df_wave1.sort_values('date').groupby('fips').last().reset_index()
df_wave2_final = df_wave2.sort_values('date').groupby('fips').last().reset_index()

print(f"1. vlna okresy: {len(df_wave1_final)}")
print(f"2. vlna okresy: {len(df_wave2_final)}")

# 4. Sloučení
df_merged = df_wave1_final.merge(
    df_wave2_final[['fips', 'deaths']], 
    on='fips', 
    suffixes=('_wave1', '_wave2'),
    how='inner'
)

# 5. Výpočet přírůstku
df_merged['deaths_increase'] = df_merged['deaths_wave2'] - df_merged['deaths_wave1']
df_merged['deaths_per_100k_increase'] = (df_merged['deaths_increase'] / df_merged['total_population']) * 100000

# 6. Filtrování
df_mining = df_merged[df_merged['income_category'] != 'Unknown'].copy()
df_mining = df_mining[df_mining['poverty_category'] != 'Unknown'].copy()
df_mining = df_mining[df_mining['deaths_per_100k_increase'] > 0].copy()

print(f"Po filtrování: {len(df_mining)}")

# 7. Kategorizace
median_pop = df_mining['total_population'].median()
df_mining['county_size'] = df_mining['total_population'].apply(
    lambda x: 'Large County' if x > median_pop else 'Small County'
)

# Target: Přírůstek úmrtnosti (5 kategorií)
df_mining['deaths_increase_ordinal'] = pd.qcut(
    df_mining['deaths_per_100k_increase'], 
    q=5,
    labels=['1_Very Small', '2_Small', '3_Medium', '4_Large', '5_Very Large'], 
    duplicates='drop'
)
df_mining['deaths_increase_ordinal'] = df_mining['deaths_increase_ordinal'].astype(str)

print("\n=== Distribuce ===")
print(df_mining['deaths_increase_ordinal'].value_counts().sort_index())

# 8. Výběr dat
df_cfminer = df_mining[[
    'deaths_increase_ordinal',
    'income_category',
    'poverty_category',
    'county_size'
]].copy()

# 9. CF-Miner - Větší zhoršení (S_Up)
print("\n=== CF-MINER: Kde se úmrtnost mezi vlnami ZHORŠILA nejvíc? ===")
clm = cleverminer(
    df=df_cfminer,
    target='deaths_increase_ordinal',
    proc='CFMiner',
    quantifiers={'S_Up': 1, 'Base': 800},
    cond={
        'attributes': [
            {'name': 'income_category', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
            {'name': 'poverty_category', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
            {'name': 'county_size', 'type': 'subset', 'minlen': 1, 'maxlen': 1}
        ], 
        'minlen': 1, 
        'maxlen': 2,
        'type': 'con'
    }
)

# 10. Výstup
output = io.StringIO()
sys.stdout = output

print("=== TEMPORAL ANALYSIS: Where mortality WORSENED between waves ===\n")
print("Wave 1: March-June 2020")
print("Wave 2: September-December 2020\n")

clm.print_summary()
print("\n")
clm.print_rulelist()

for i in range(1, len(clm.rulelist) + 1):
    print(f"\n=== Rule {i} ===")
    clm.print_rule(i)

sys.stdout = sys.__stdout__

with open("CFMiner_2.txt", "w", encoding="utf-8") as f:
    f.write(output.getvalue())

print("\n" + output.getvalue())
print("\nVýstup uložen jako CFMiner_2.txt")