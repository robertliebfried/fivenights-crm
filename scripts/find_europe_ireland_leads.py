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

# Exclude USA, Germany, Australia
excluded_countries = ['United States', 'Germany', 'Australia']
df_eu = df[~df['Country'].isin(excluded_countries)].copy()

print(f"Total leads in Europe & Other (excluding USA, Germany, Australia): {len(df_eu)}")
print("\nCountry breakdown:")
print(df_eu['Country'].value_counts())

# Now let's see which ones have recovery/claims/dispute/guard/litigation/law/solicitors/advocate/forensic keywords
pattern_keywords = r'(?i)\b(recovery|claim|claims|guard|dispute|disputes|debt|forensic|restitution|tracing|litigation|solicitor|solicitors|law|legal|advocate|advocates|barrister|juridique|contentieux|avocat|abogado)\b'

matches = df_eu[
    (df_eu['Company name'].str.contains(pattern_keywords, na=False, regex=True)) |
    (df_eu['Organization type'].str.contains(r'(?i)solicitor|law|legal|advocacy|claims', na=False, regex=True)) |
    (df_eu['Recovery or disputes relevance'].str.contains(r'(?i)litigation|claims|forensic|dispute', na=False, regex=True))
].copy()

print(f"\nTotal high-intent recovery/claims/litigation leads in Europe & Ireland: {len(matches)}")
print("\nBreakdown by Country:")
print(matches['Country'].value_counts())

print("\nBreakdown by Relevance:")
print(matches['Recovery or disputes relevance'].value_counts())
