import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree, export_text
from sklearn.metrics import accuracy_score, classification_report

# =============================================================================
# 1. PŘÍPRAVA DAT (Stejná čistka jako předtím)
# =============================================================================
df = pd.read_csv('merged_data.csv', delimiter=',', engine='python', on_bad_lines='skip')

# Převod data a výběr posledního záznamu (aby 1 řádek = 1 okres)
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by=['fips', 'date'])
    df_final = df.drop_duplicates(subset=['fips'], keep='last').copy()
else:
    df_final = df.copy() # Pokud už je to agregované

# =============================================================================
# 2. DEFINICE CÍLE A PROMĚNNÝCH
# =============================================================================

# CÍL (Target): Chceme předpovídat, jestli je úmrtnost (CFR) Vysoká nebo Nízká
# Rozdělíme mediánem (nebo můžeš dát fixní hranici, např. 2 %)
median_cfr = df_final['case_fatality_rate_pct'].median()
df_final['Target_Label'] = df_final['case_fatality_rate_pct'].apply(lambda x: 1 if x > median_cfr else 0)
# 1 = Vysoká úmrtnost, 0 = Nízká úmrtnost

# PŘÍZNAKY (Features): Podle čeho to chceme poznat?
# Pro strom je LEPŠÍ použít přesná čísla, ne kategorie. On si najde přesný bod zlomu.
feature_cols = [
    'median_household_income',     # Příjem
    'poverty_percent_all_ages',    # Chudoba
    'total_population',            # Velikost okresu
    'pct_black',                   # Podíl afroameričanů (pokud nemáš, dopočítáme)
    'pct_hispanic',                # Podíl hispánců
    'pct_white'                    # Podíl bělochů
]

# Rychlé dopočítání procent, pokud chybí (jako v minulém kroku)
if 'pct_black' not in df_final.columns and 'black_alone_male' in df_final.columns:
    df_final['pct_black'] = (df_final['black_alone_male'] + df_final['black_alone_female']) / df_final['total_population'] * 100
    df_final['pct_hispanic'] = (df_final['hispanic_male'] + df_final['hispanic_female']) / df_final['total_population'] * 100
    df_final['pct_white'] = (df_final['white_alone_male'] + df_final['white_alone_female']) / df_final['total_population'] * 100

# Vyčištění od NaN (strom nesmí mít díry v datech)
df_model = df_final[feature_cols + ['Target_Label']].dropna()

X = df_model[feature_cols] # Vstupy
y = df_model['Target_Label'] # Výstup

# Rozdělení na trénovací a testovací sadu (80% na učení, 20% na test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# =============================================================================
# 3. TRÉNOVÁNÍ STROMU
# =============================================================================
# max_depth=3: Důležité pro interpretaci! Nechceme obří "křoví", ale jednoduchý strom, co přečteme.
clf = DecisionTreeClassifier(max_depth=3, random_state=42)
clf.fit(X_train, y_train)

# =============================================================================
# 4. VYHODNOCENÍ A INTERPRETACE
# =============================================================================

# Jak je model přesný?
y_pred = clf.predict(X_test)
print(f"Přesnost modelu (Accuracy): {accuracy_score(y_test, y_pred):.2%}")
print("\nCo je pro model nejdůležitější (Feature Importance):")
importances = pd.DataFrame({'Feature': feature_cols, 'Importance': clf.feature_importances_})
print(importances.sort_values(by='Importance', ascending=False))

# =============================================================================
# 5. VIZUALIZACE (To je ta "interpretace")
# =============================================================================
print("\n=== TEXTOVÁ PODOBA STROMU ===")
# Ukáže pravidla typu: "Když Income <= 45000 tak..."
tree_rules = export_text(clf, feature_names=feature_cols)
print(tree_rules)

# Grafické vykreslení (uloží se jako obrázek)
plt.figure(figsize=(20,10))
plot_tree(clf, feature_names=feature_cols, class_names=['Low Mortality', 'High Mortality'], filled=True, fontsize=10)
plt.title("Rozhodovací strom: Predikce úmrtí na COVID-19 (2020)")
plt.savefig("rozhodovaci_strom.png")
print("\nGraf stromu byl uložen jako 'rozhodovaci_strom.png'")