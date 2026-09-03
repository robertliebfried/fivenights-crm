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

# Exclude USA, Germany, Australia, Ireland, and non-Europe
excluded = ['United States', 'Germany', 'Australia', 'Ireland', 'Canada', 'New Zealand', 'Hong Kong', 'Japan', 'Singapore']
df_eu = df[~df['Country'].isin(excluded)].copy()

print(f"Total available European leads (excluding US, DE, AU, IE): {len(df_eu)}")

# Search for high-intent keywords in company name or organization type
# Recovery, Claims, Dispute, Law, Legal, Solicitor, Asset, Fraud, Forensic, Restructuring, Counsel, Chambers, Litigation
pattern = r'(?i)\b(recovery|claim|claims|dispute|disputes|asset|assets|fraud|forensic|investig|litigat|law|legal|solicitor|solicitors|chambers|counsel|advocat|avocat|abogado|juridique|contentieux|restitution|debt)\b'

matches = df_eu[
    df_eu['Company name'].str.contains(pattern, na=False, regex=True) |
    df_eu['Organization type'].str.contains(pattern, na=False, regex=True) |
    df_eu['Recovery or disputes relevance'].str.contains(r'(?i)litigation|claims|forensic|dispute', na=False, regex=True)
].copy()

print(f"Total matches found: {len(matches)}")
print("\nBreakdown by country:")
print(matches['Country'].value_counts())

# Group by country and inspect the top names
for country in ['United Kingdom', 'Switzerland', 'Cyprus', 'Malta', 'Netherlands', 'Sweden', 'Denmark', 'Estonia', 'Luxembourg', 'Spain', 'France']:
    sub = matches[matches['Country'] == country]
    print(f"\n==================== {country} ({len(sub)} leads) ====================")
    for idx, r in sub.head(15).reset_index(drop=True).iterrows():
        print(f"[{idx+1}] {r['Company name']}")
        print(f"    Regulator: {r['Regulator or professional body']} | Lic: {r['Licence / register number']}")
        print(f"    Scope: {r['Recovery or disputes relevance']}")
        print(f"    City: {r.get('City / address', '')}")
        print(f"    Source URL: {r.get('Official source URL', '')}")
