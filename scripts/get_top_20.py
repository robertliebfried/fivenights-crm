import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

excel_path = r'C:\Users\User\Documents\org\ONE_BIG_WORLDWIDE_LICENSED_LEADS_2026-08-28.xlsx'
df = pd.read_excel(excel_path, sheet_name='Direct Recovery & Litigation')

# Pick top 20 verified leads across key jurisdictions (Ireland, UK, Australia, Germany, Switzerland)
selected = []

# 1. Ireland (Law Society of Ireland - licensed solicitors with litigation rights)
ireland = df[(df['Country'] == 'Ireland') & (df['Recovery or disputes relevance'] == 'Legal representation / litigation possible')]
selected.extend(ireland.head(8).to_dict('records'))

# 2. United Kingdom (SRA / FCA - legal litigation & claims management)
uk = df[df['Country'] == 'United Kingdom']
selected.extend(uk.head(4).to_dict('records'))

# 3. Australia (ASIC - Claims handling / AFSL dispute resolution)
aus = df[(df['Country'] == 'Australia') & (df['Recovery or disputes relevance'] == 'Claims handling / insurance claims authorization')]
selected.extend(aus.head(4).to_dict('records'))

# 4. Germany & Switzerland (BaFin / VQF / ARIF - Debt recovery / Krypto / Forensics)
eu = df[df['Country'].isin(['Germany', 'Switzerland', 'Netherlands'])]
selected.extend(eu.head(4).to_dict('records'))

print("=== TOP 20 FUNDS RECOVERY & LITIGATION LEADS ===")
for i, r in enumerate(selected[:20], 1):
    email_str = r.get('Email', '') if pd.notna(r.get('Email')) else 'Verify via registry'
    phone_str = r.get('Phone', '') if pd.notna(r.get('Phone')) else '-'
    city_str = r.get('City / address', '') if pd.notna(r.get('City / address')) else r.get('Country', '')
    licence = r.get('Licence / register number', '')
    regulator = r.get('Regulator or professional body', '')
    company = r.get('Company name', '')
    relevance = r.get('Recovery or disputes relevance', '')
    
    print(f"{i}. {company}")
    print(f"   Country: {r.get('Country')} | City: {city_str}")
    print(f"   Regulator: {regulator} | Licence/Reg: {licence}")
    print(f"   Authority: {relevance}")
    print(f"   Email: {email_str} | Phone: {phone_str}")
    print(f"   Google Search: \"{company}\" \"{regulator}\"")
    print("-" * 65)
