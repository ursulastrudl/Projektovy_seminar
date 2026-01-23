import pandas as pd
from cleverminer import cleverminer
import io
import sys


df = pd.read_csv('merged_data.csv', delimiter=',', engine='python', on_bad_lines='skip')
df = df.sort_values(by=['fips', 'date'])
df_final = df.drop_duplicates(subset=['fips'], keep='last').copy()

print(f"Finální počet okresů: {len(df_final)}")


df_final['black_total'] = df_final['black_alone_male'] + df_final['black_alone_female']
df_final['black_percent'] = (df_final['black_total'] / df_final['total_population']) * 100


df_mining = df_final[df_final['income_category'] != 'Unknown'].copy()
df_mining = df_mining[df_mining['poverty_category'] != 'Unknown'].copy()
df_mining = df_mining[df_mining['case_fatality_rate_pct'].notna()].copy()
df_mining = df_mining[df_mining['black_percent'].notna()].copy()

print(f"Po filtrování: {len(df_mining)}")

p33 = df_mining['black_percent'].quantile(0.33)
p67 = df_mining['black_percent'].quantile(0.67)

def categorize_black(val):
    if val <= p33:
        return 'Low Black Population'
    elif val >= p67:
        return 'High Black Population'
    else:
        return 'Medium Black Population'

df_mining['black_category'] = df_mining['black_percent'].apply(categorize_black)


median_cfr = df_mining['case_fatality_rate_pct'].median()
df_mining['CFR_Category'] = df_mining['case_fatality_rate_pct'].apply(
    lambda x: 'High CFR' if x > median_cfr else 'Low CFR'
)


df_mining['deaths_per_100k'] = (df_mining['deaths'] / df_mining['total_population']) * 100000
median_deaths = df_mining['deaths_per_100k'].median()
df_mining['deaths_category'] = df_mining['deaths_per_100k'].apply(
    lambda x: 'High Deaths' if x > median_deaths else 'Low Deaths'
)

df_cfr = df_mining[['black_category', 'income_category', 'poverty_category', 'CFR_Category']]

clm_cfr = cleverminer(
    df=df_cfr,
    proc='4ftMiner',
    quantifiers={'Base': 200, 'aad': 0.15},
    ante={
        'attributes': [
            {'name': 'black_category', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
            {'name': 'income_category', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
            {'name': 'poverty_category', 'type': 'subset', 'minlen': 1, 'maxlen': 1}
        ], 'minlen': 1, 'maxlen': 2, 'type': 'con'
    },
    succ={
        'attributes': [
            {'name': 'CFR_Category', 'type': 'subset', 'minlen': 1, 'maxlen': 1}
        ], 'minlen': 1, 'maxlen': 1, 'type': 'con'
    }
)


clm_cfr.print_rulelist()

df_deaths = df_mining[['black_category', 'income_category', 'poverty_category', 'deaths_category']]

clm_deaths = cleverminer(
    df=df_deaths,
    proc='4ftMiner',
    quantifiers={'Base': 200, 'aad': 0.15},
    ante={
        'attributes': [
            {'name': 'black_category', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
            {'name': 'income_category', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
            {'name': 'poverty_category', 'type': 'subset', 'minlen': 1, 'maxlen': 1}
        ], 'minlen': 1, 'maxlen': 2, 'type': 'con'
    },
    succ={
        'attributes': [
            {'name': 'deaths_category', 'type': 'subset', 'minlen': 1, 'maxlen': 1}
        ], 'minlen': 1, 'maxlen': 1, 'type': 'con'
    }
)


clm_deaths.print_rulelist()


output = io.StringIO()
sys.stdout = output

print("=== RACIAL DISPARITIES IN COVID-19 MORTALITY ===")
print("Research Question: Do counties with higher Black population have higher COVID-19 mortality?\n")

print("=== CFR Analysis ===")
clm_cfr.print_summary()
clm_cfr.print_rulelist()

print("\n\n=== Deaths per 100k Analysis ===")
clm_deaths.print_summary()
clm_deaths.print_rulelist()

print("\n\n=== Detailed Rules - CFR ===")
for i in range(1, len(clm_cfr.rulelist) + 1):
    print(f"\n=== CFR Rule {i} ===")
    clm_cfr.print_rule(i)

print("\n\n=== Detailed Rules - Deaths ===")
for i in range(1, len(clm_deaths.rulelist) + 1):
    print(f"\n=== Deaths Rule {i} ===")
    clm_deaths.print_rule(i)

sys.stdout = sys.__stdout__

with open("4ftminer_2_output.txt", "w", encoding="utf-8") as f:
    f.write(output.getvalue())

print("\n" + output.getvalue())
print("\nVýstup uložen jako 4ftminer_2_output.txt")
