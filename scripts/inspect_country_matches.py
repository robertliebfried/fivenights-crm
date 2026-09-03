import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

excel_path = r'C:\Users\User\Documents\org\ONE_BIG_WORLDWIDE_LICENSED_LEADS_2026-08-28.xlsx'
df_target = pd.read_excel(excel_path, sheet_name='Direct Recovery & Litigation')
df_all = pd.read_excel(excel_path, sheet_name='All Leads')

df = pd.concat([df_target, df_all], ignore_index=True).drop_duplicates(
    subset=['Company name', 'Country', 'Regulator or professional body', 'Licence / register number']
)

pattern = r'(?i)\b(recovery|claim|claims|guard|dispute|disputes|forensic|debt|restitution)\b'
matches = df[df['Company name'].str.contains(pattern, na=False, regex=True)].copy()

print("Counts by country:")
print(matches['Country'].value_counts())

print("\n--- Non-Australia top matches ---")
non_aus = matches[matches['Country'] != 'Australia']
for idx, r in non_aus.iterrows():
    print(f"{r['Company name']} | {r['Country']} | {r['Regulator or professional body']} | Lic: {r['Licence / register number']} | Email: {r.get('Email', '')}")

print("\n--- Australia top highlights (Claims / Recovery / Guard) ---")
aus_highlights = matches[matches['Country'] == 'Australia']
for idx, r in aus_highlights.head(25).iterrows():
    print(f"{r['Company name']} | {r['Regulator or professional body']} | Lic: {r['Licence / register number']}")
