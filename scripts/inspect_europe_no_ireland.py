import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

excel_path = r'C:\Users\User\Documents\org\ONE_BIG_WORLDWIDE_LICENSED_LEADS_2026-08-28.xlsx'
df_target = pd.read_excel(excel_path, sheet_name='Direct Recovery & Litigation')
df_all = pd.read_excel(excel_path, sheet_name='All Leads')

df = pd.concat([df_target, df_all], ignore_index=True).drop_duplicates(
    subset=['Company name', 'Country', 'Regulator or professional body', 'Licence / register number']
)

# Exclude USA, Germany, Australia, Ireland, and non-Europe (Canada, NZ, Hong Kong, Japan, Singapore)
excluded = ['United States', 'Germany', 'Australia', 'Ireland', 'Canada', 'New Zealand', 'Hong Kong', 'Japan', 'Singapore']
df_eu_no_ireland = df[~df['Country'].isin(excluded)].copy()

print(f"Total leads remaining: {len(df_eu_no_ireland)}")
print("\nCountry breakdown:")
print(df_eu_no_ireland['Country'].value_counts())

# Check Direct Recovery & Litigation sheet specifically for these countries
df_target_filtered = df_target[~df_target['Country'].isin(excluded)].copy()
print(f"\nDirect Recovery & Litigation leads count (no US/DE/AU/IE): {len(df_target_filtered)}")
print(df_target_filtered['Country'].value_counts())
print("\nRelevance in Direct Recovery sheet:")
print(df_target_filtered['Recovery or disputes relevance'].value_counts())

print("\n--- All Direct Recovery Leads (no US/DE/AU/IE) ---")
for idx, r in df_target_filtered.iterrows():
    print(f"[{r['Country']}] {r['Company name']}")
    print(f"   Regulator: {r['Regulator or professional body']} | Lic: {r['Licence / register number']}")
    print(f"   Relevance: {r['Recovery or disputes relevance']}")
    print(f"   Email: {r.get('Email', '')} | Phone: {r.get('Phone', '')}")
    print("-" * 60)
