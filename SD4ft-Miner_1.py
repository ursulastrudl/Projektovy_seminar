import pandas as pd
from cleverminer import cleverminer
import io
import sys

# 1. Načtení dat
df = pd.read_csv('merged_data.csv', delimiter=',', engine='python', on_bad_lines='skip')
df = df.sort_values(by=['fips', 'date'])
df_final = df.drop_duplicates(subset=['fips'], keep='last').copy()

print(f"Finální počet okresů: {len(df_final)}")

# 2. Filtrování
df_mining = df_final[df_final['case_fatality_rate_pct'].notna()].copy()

# 3. Vytvoření jednoduchých kategorií

# Gender - medián
median_female = df_mining['total_female'].median()
median_total = df_mining['total_population'].median()
female_percent_median = (median_female / median_total) * 100

df_mining['female_percent'] = (df_mining['total_female'] / df_mining['total_population']) * 100
df_mining['gender_group'] = df_mining['female_percent'].apply(
    lambda x: 'More Females' if x > female_percent_median else 'More Males'
)

# County size - medián
median_pop = df_mining['total_population'].median()
df_mining['county_size'] = df_mining['total_population'].apply(
    lambda x: 'Large' if x > median_pop else 'Small'
)

# CFR - medián
median_cfr = df_mining['case_fatality_rate_pct'].median()
df_mining['CFR_level'] = df_mining['case_fatality_rate_pct'].apply(
    lambda x: 'High CFR' if x > median_cfr else 'Low CFR'
)

print(f"Po filtrování: {len(df_mining)}")

# 4. Distribuce
print("\n=== Distribuce ===")
print("\nGender Group:")
print(df_mining['gender_group'].value_counts())
print("\nCounty Size:")
print(df_mining['county_size'].value_counts())
print("\nCFR Level:")
print(df_mining['CFR_level'].value_counts())

# 5. Výběr dat
df_sd4ft = df_mining[['gender_group', 'county_size', 'CFR_level']].copy()

print(f"\nData pro SD4ft: {len(df_sd4ft)} rows")

# 6. SD4ft-Miner
print("\n=== SD4FT-MINER ===")

clm = cleverminer(
    df=df_sd4ft,
    proc='SD4ftMiner',
    quantifiers={
        'Base1': 100,
        'Base2': 100,
        'Ratiopim': 1.3
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
    frst={
        'attributes': [
            {'name': 'gender_group', 'type': 'subset', 'minlen': 1, 'maxlen': 1}
        ], 
        'minlen': 1, 
        'maxlen': 1,
        'type': 'con'
    },
    scnd={
        'attributes': [
            {'name': 'gender_group', 'type': 'subset', 'minlen': 1, 'maxlen': 1}
        ], 
        'minlen': 1, 
        'maxlen': 1,
        'type': 'con'
    }
)

# 7. Výstup
output = io.StringIO()
sys.stdout = output

print("=== SD4FT-MINER: Gender Differences ===\n")
print("Comparing: More Females vs More Males\n")

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