import pandas as pd
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

excel_path = r'C:\Users\User\Documents\org\ONE_BIG_WORLDWIDE_LICENSED_LEADS_2026-08-28.xlsx'
df_target = pd.read_excel(excel_path, sheet_name='Direct Recovery & Litigation')
df_all = pd.read_excel(excel_path, sheet_name='All Leads')

df = pd.concat([df_target, df_all], ignore_index=True).drop_duplicates(
    subset=['Company name', 'Country', 'Regulator or professional body', 'Licence / register number']
)

# Search patterns
pattern = r'(?i)\b(recovery|claim|claims|guard|dispute|disputes|debt|forensic|restitution|tracing|asset recovery|settlement)\b'

matches = df[df['Company name'].str.contains(pattern, na=False, regex=True)].copy()

print(f"Total matching companies found: {len(matches)}")
print("\nSample matching names:")
for idx, r in matches.head(40).reset_index(drop=True).iterrows():
    c_name = r['Company name']
    country = r['Country']
    reg = r['Regulator or professional body']
    lic = r['Licence / register number']
    rel = r['Recovery or disputes relevance']
    email = r.get('Email', '')
    phone = r.get('Phone', '')
    city = r.get('City / address', '')
    print(f"[{idx+1}] {c_name} | {country}")
    print(f"    Regulator: {reg} | Lic: {lic}")
    print(f"    Scope/Relevance: {rel}")
    print(f"    Email: {email} | Phone: {phone} | City: {city}")
    print("-" * 60)
