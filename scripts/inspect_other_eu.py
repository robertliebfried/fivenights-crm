import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

excel_path = r'C:\Users\User\Documents\org\ONE_BIG_WORLDWIDE_LICENSED_LEADS_2026-08-28.xlsx'
df = pd.read_excel(excel_path, sheet_name='All Leads')

# Exclude USA, Germany, Australia, Ireland, Canada, NZ, Hong Kong, Japan, Singapore
excluded = ['United States', 'Germany', 'Australia', 'Ireland', 'Canada', 'New Zealand', 'Hong Kong', 'Japan', 'Singapore']
df_eu = df[~df['Country'].isin(excluded)].copy()

# Print counts and sample from Switzerland, Spain, Luxembourg, etc.
print("Total EU remaining in All Leads:", len(df_eu))
print(df_eu['Country'].value_counts())

print("\n--- Switzerland samples ---")
for idx, r in df_eu[df_eu['Country'] == 'Switzerland'].head(10).iterrows():
    print(f"{r['Company name']} | {r['Regulator or professional body']} | {r['Licence / register number']} | {r['Recovery or disputes relevance']}")

print("\n--- Spain samples ---")
for idx, r in df_eu[df_eu['Country'] == 'Spain'].head(10).iterrows():
    print(f"{r['Company name']} | {r['Regulator or professional body']} | {r['Licence / register number']} | {r['Recovery or disputes relevance']}")

print("\n--- Other EU countries ---")
other_eu = df_eu[~df_eu['Country'].isin(['France', 'Spain', 'Switzerland', 'United Kingdom'])]
for idx, r in other_eu.iterrows():
    print(f"[{r['Country']}] {r['Company name']} | {r['Regulator or professional body']} | {r['Licence / register number']} | {r['Recovery or disputes relevance']}")
