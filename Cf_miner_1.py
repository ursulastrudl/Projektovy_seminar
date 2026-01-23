import pandas as pd
from cleverminer import cleverminer
import io
import sys

df = pd.read_csv('merged_data.csv', delimiter=',', engine='python', on_bad_lines='skip')
df = df.sort_values(by=['fips', 'date'])
df_final = df.drop_duplicates(subset=['fips'], keep='last').copy()

print(f"Finální počet okresů: {len(df_final)}")


df_mining = df_final[df_final['income_category'] != 'Unknown'].copy()
df_mining = df_mining[df_mining['poverty_category'] != 'Unknown'].copy()
df_mining = df_mining[df_mining['case_fatality_rate_pct'].notna()].copy()


p33_pop = df_mining['total_population'].quantile(0.33)
p67_pop = df_mining['total_population'].quantile(0.67)

def categorize_population(val):
    if val <= p33_pop:
        return 'Small County'
    elif val >= p67_pop:
        return 'Large County'
    else:
        return 'Medium County'

df_mining['county_size'] = df_mining['total_population'].apply(categorize_population)

df_mining['female_percent'] = (df_mining['total_female'] / df_mining['total_population']) * 100
median_female = df_mining['female_percent'].median()
df_mining['gender_category'] = df_mining['female_percent'].apply(
    lambda x: 'Higher Female %' if x > median_female else 'Lower Female %'
)


df_mining['CFR_ordinal'] = pd.qcut(
    df_mining['case_fatality_rate_pct'], 
    q=5,
    
    labels=['1_Very Low', '2_Low', '3_Medium', '4_High', '5_Very High'],
    duplicates='drop'
)

df_mining['CFR_ordinal'] = df_mining['CFR_ordinal'].astype(str)

print(f"Po filtrování: {len(df_mining)}")

print("\n=== CFR Distribution ===")
print(f"Mean CFR: {df_mining['case_fatality_rate_pct'].mean():.3f}%")
print(f"Median CFR: {df_mining['case_fatality_rate_pct'].median():.3f}%")
print(f"Min CFR: {df_mining['case_fatality_rate_pct'].min():.3f}%")
print(f"Max CFR: {df_mining['case_fatality_rate_pct'].max():.3f}%")

print("\n=== Category Distributions ===")
print("\nCFR Ordinal (TARGET):")
print(df_mining['CFR_ordinal'].value_counts().sort_index())
print("\nIncome Category:")
print(df_mining['income_category'].value_counts())
print("\nPoverty Category:")
print(df_mining['poverty_category'].value_counts())
print("\nCounty Size:")
print(df_mining['county_size'].value_counts())
print("\nGender Category:")
print(df_mining['gender_category'].value_counts())


df_cfminer = df_mining[[
    'CFR_ordinal',  
    'income_category',
    'poverty_category',
    'county_size',
    'gender_category'
]].copy()

print(f"\nFinální data pro CF-Miner: {len(df_cfminer)} rows")


print("\n\n=== CF-MINER: Podmínky s poklesem úmrtnosti ===")

clm_down = cleverminer(
    df=df_cfminer,
    target='CFR_ordinal',  
    proc='CFMiner',
    quantifiers={'S_Down': 1, 'Base': 100},  
    cond={
        'attributes': [
            {'name': 'income_category', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
            {'name': 'poverty_category', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
            {'name': 'county_size', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
            {'name': 'gender_category', 'type': 'subset', 'minlen': 1, 'maxlen': 1}
        ], 
        'minlen': 1, 
        'maxlen': 2,  
        'type': 'con'
    }
)

print("=== Rules: Conditions where CFR is DECLINING ===")
clm_down.print_rulelist()




output = io.StringIO()
sys.stdout = output

print("=" * 80)
print("CF-MINER ANALYSIS: Where Do We See Decline in COVID-19 Mortality?")
print("=" * 80)
print("\nResearch Question: What conditions are associated with LOWER mortality rates?")
print("(Looking for protective factors)\n")

print("=== DECLINING MORTALITY (S_Down) ===")
print("\nSummary:")
clm_down.print_summary()
print("\nRules:")
clm_down.print_rulelist()

print("\n\nDetailed Rules:")
for i in range(1, len(clm_down.rulelist) + 1):
    print(f"\n--- Rule {i} (DECLINE) ---")
    clm_down.print_rule(i)

sys.stdout = sys.__stdout__

# Uložení
with open("Cf_miner_1.py.txt", "w", encoding="utf-8") as f:
    f.write(output.getvalue())

print("\n" + output.getvalue())
print("\nVýstup uložen jako Cf_miner_1.py.txt")