import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

excel_path = r'C:\Users\User\Documents\org\ONE_BIG_WORLDWIDE_LICENSED_LEADS_2026-08-28.xlsx'
df_target = pd.read_excel(excel_path, sheet_name='Direct Recovery & Litigation')
df_all = pd.read_excel(excel_path, sheet_name='All Leads')

df = pd.concat([df_target, df_all], ignore_index=True).drop_duplicates(
    subset=['Company name', 'Country', 'Regulator or professional body', 'Licence / register number']
)

# Exclude USA, Germany, Australia
excluded = ['United States', 'Germany', 'Australia']
df_filtered = df[~df['Country'].isin(excluded)].copy()

# 1. European Recovery / Claims / Dispute firms
eu_claims_pattern = r'(?i)\b(recovery|claim|claims|dispute|disputes|debt|forensic)\b'
eu_claims = df_filtered[df_filtered['Company name'].str.contains(eu_claims_pattern, na=False, regex=True)]

# 2. Ireland top solicitors with direct email and phone
ireland = df_filtered[df_filtered['Country'] == 'Ireland'].dropna(subset=['Email'])

print("Found European claims firms:", len(eu_claims))
print("Found Ireland licensed firms with email:", len(ireland))
