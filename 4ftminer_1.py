import pandas as pd
from cleverminer import cleverminer
import io
import sys


df = pd.read_csv('merged_data.csv', delimiter=',', engine='python', on_bad_lines='skip')
df = df.sort_values(by=['fips', 'date'])
df_final = df.drop_duplicates(subset=['fips'], keep='last').copy()

print(f"Původní počet řádků (denní): {len(df)}")
print(f"Finální počet okresů: {len(df_final)}")

df_mining = df_final[df_final['income_category'] != 'Unknown'].copy()
df_mining = df_mining[df_mining['poverty_category'] != 'Unknown'].copy()


df_mining = df_mining[df_mining['case_fatality_rate_pct'].notna()].copy()
print(f"Po odstranění NaN v CFR: {len(df_mining)}")


df_mining['CFR_Category'] = pd.qcut(
    df_mining['case_fatality_rate_pct'], 
    q=3, 
    labels=['Low', 'Medium', 'High']
)
df_mining['CFR_Category'] = df_mining['CFR_Category'].astype(str)


df_mining = df_mining[['income_category', 'poverty_category', 'CFR_Category']]

print(f"\nFinální počet řádků pro mining: {len(df_mining)}")

clm = cleverminer(
    df=df_mining,
    proc='4ftMiner',
    quantifiers={'Base': 500, 'aad': 0.1}, 
    ante={
        'attributes': [
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

# Zachycení výstupu
output = io.StringIO()
sys.stdout = output

print("=== Shrnutí ===")
clm.print_summary()
print("\n=== Seznam pravidel ===")
clm.print_rulelist()
print("\n=== Jednotlivá pravidla ===")
for i in range(1, len(clm.rulelist) + 1):
    print(f"\n=== Rule {i} ===\n")
    clm.print_rule(i)

sys.stdout = sys.__stdout__

# Uložení výstupu
with open("4ftMiner_question1_output.txt", "w", encoding="utf-8") as f:
    f.write(output.getvalue())

print("\n" + output.getvalue())
print("\nVýstup uložen jako 4ftMiner_question1_output.txt")