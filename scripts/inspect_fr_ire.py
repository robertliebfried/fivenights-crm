import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

excel_path = r'C:\Users\User\Documents\org\ONE_BIG_WORLDWIDE_LICENSED_LEADS_2026-08-28.xlsx'
df = pd.read_excel(excel_path, sheet_name='All Leads')

# Check France and Spain for any legal/recovery/dispute/patrimoine keywords
france_matches = df[df['Country'] == 'France']
print("France total:", len(france_matches))
fr_patrimoine = france_matches[france_matches['Company name'].str.contains(r'(?i)conseil|gestion|patrimoine|finance|avocat|juridique', na=False, regex=True)]
print("France advisory/patrimoine:", len(fr_patrimoine))

# Ireland
ireland = df[df['Country'] == 'Ireland']
print("Ireland total:", len(ireland))
print("Ireland with email:", ireland['Email'].dropna().count())
print("Ireland with phone:", ireland['Phone'].dropna().count())
print("Ireland sample names:")
for idx, r in ireland.head(15).iterrows():
    print(f" - {r['Company name']} | Reg: {r['Licence / register number']} | Email: {r['Email']} | Phone: {r['Phone']} | City: {r['City / address']}")
