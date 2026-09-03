import sys
import os
import re
import datetime
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

sys.stdout.reconfigure(encoding='utf-8')

print("Starting consolidated leads generator...")

# 1. Load existing v2 file
v2_path = r'C:\Users\User\Downloads\ONE_BIG_WORLDWIDE_LICENSED_LEADS_2026-08-27_v2.xlsx'
df_v2 = pd.read_excel(v2_path)

# Drop any non-data trailing rows
df_v2 = df_v2.dropna(subset=['Company'])
df_v2 = df_v2[df_v2['Company'].astype(str).str.strip() != '']
# Filter out any header notes placed in data rows
df_v2 = df_v2[~df_v2['Priority'].astype(str).str.startswith('Filter by')]

print(f"Loaded {len(df_v2)} rows from existing v2 workbook.")

# Map existing columns to 21 standard columns
# Standard Columns:
# 1. Priority
# 2. Country
# 3. Company name
# 4. Organization type
# 5. Regulator or professional body
# 6. Licence / register number
# 7. Licence or registration status
# 8. Status checked date
# 9. Source date
# 10. Licence scope / permitted services
# 11. Recovery or disputes relevance
# 12. Website URL
# 13. Website status
# 14. Website verification method
# 15. Email
# 16. Phone
# 17. City / address
# 18. Official source URL
# 19. Source file or dataset
# 20. Confidence
# 21. Next verification action

def clean_text(val):
    if pd.isna(val):
        return ""
    s = str(val).strip()
    # Clean common replacement character artifacts
    s = s.replace('\ufffd', ' ')
    s = re.sub(r'\s+', ' ', s)
    return s

def map_relevance(scope_text, type_text, country):
    scope = str(scope_text).lower()
    t = str(type_text).lower()
    if 'litigation' in scope or 'claims / consumer' in scope or 'law firm' in t or 'solicitor' in t or 'legal' in scope:
        return "Legal representation / litigation possible"
    elif 'claims handling' in scope or 'claims settling' in scope or 'claims' in t:
        return "Claims handling / insurance claims authorization"
    elif 'crypto' in scope or 'krypto' in scope or 'casp' in t or 'vasp' in t:
        return "Crypto-asset services authorization"
    elif 'payment' in scope or 'transaction' in scope or 'zahlungs' in scope:
        return "Payment / transaction-dispute capability"
    elif 'forensic' in scope or 'investigat' in scope or 'tracing' in scope:
        return "Forensic / investigative / asset-tracing service indicated"
    elif 'investment advice' in scope or 'financial product advice' in scope or 'portfolio' in scope or 'cif' in t or 'eaf' in t:
        return "Financial or investment advice authorization"
    elif 'financial' in scope or 'financial' in t:
        return "General financial authorization; recovery authority not established"
    else:
        return "Status or scope requires re-verification"

def map_regulator_full(reg, country):
    r = str(reg).strip()
    if r == 'ASIC':
        return 'Australian Securities and Investments Commission (ASIC)'
    elif r == 'ORIAS / French Treasury registry':
        return 'ORIAS (Registre unique des intermédiaires en assurance, banque et finance) / French Treasury'
    elif r == 'Law Society of Ireland':
        return 'Law Society of Ireland'
    elif r == 'FINMA':
        return 'Swiss Financial Market Supervisory Authority (FINMA)'
    elif r == 'CNMV':
        return 'Comisión Nacional del Mercado de Valores (CNMV)'
    elif r == 'SRA':
        return 'Solicitors Regulation Authority (SRA)'
    return r

def map_source_dataset(country, regulator):
    c = str(country).lower()
    if 'australia' in c:
        return "ASIC AFS Licensee Dataset - Current (data.gov.au)"
    elif 'france' in c:
        return "ORIAS Registre unique des intermédiaires - Liste CIF (data.gouv.fr)"
    elif 'ireland' in c:
        return "Law Society of Ireland Solicitor Firm Directory"
    elif 'switzerland' in c:
        return "FINMA Authorised Institutions List - Portfolio Managers & Trustees (grfinig.xlsx)"
    elif 'spain' in c:
        return "CNMV Registro Oficial de Empresas de Asesoramiento Financiero (EAF)"
    elif 'united kingdom' in c:
        return "SRA Solicitors Register Extract"
    return "Official National Regulator Register"

def map_website_status(signal):
    sig = str(signal).lower()
    if 'no website recorded' in sig:
        return "No website recorded in source directory"
    elif 'not provided in' in sig:
        return "Not provided in source — verify manually"
    elif 'no likely official website' in sig:
        return "Manual verification required — no working website found"
    elif 'inaccessible' in sig or 'offline' in sig:
        return "Website inaccessible / offline"
    return "Not provided in source — verify manually"

def map_website_verification(signal, country):
    sig = str(signal).lower()
    if 'no website recorded' in sig:
        return "Official directory record check (no website registered)"
    elif 'not provided in' in sig:
        return "Bulk directory extract (website field not provided by registry)"
    elif 'no likely official website' in sig:
        return "Manual search / registry check (no official website identified)"
    return "Registry extract analysis"

def map_next_action(country, p):
    priority = str(p).strip()
    c = str(country).strip()
    if priority == 'High':
        return f"Verify current direct contact details and check domain availability for outreach in {c}"
    elif priority == 'Medium':
        return f"Cross-check commercial register and execute automated domain search for {c} entity"
    else:
        return f"Re-verify active licence status on official {c} regulator portal before client outreach"

existing_rows = []
for _, row in df_v2.iterrows():
    c_name = clean_text(row.get('Company', ''))
    if not c_name:
        continue
    country = clean_text(row.get('Country', ''))
    org_type = clean_text(row.get('Type', ''))
    regulator = map_regulator_full(row.get('Regulator', ''), country)
    licence_id = clean_text(row.get('Licence / Register ID', 'Not published by source'))
    if not licence_id:
        licence_id = "Not published by source"
    
    lic_status = clean_text(row.get('Active licence evidence', 'Active / Authorised'))
    checked_date = clean_text(row.get('Checked', '2026-08-28'))
    source_date = clean_text(row.get('Source date / freshness', '2026'))
    if not source_date or source_date == 'nan':
        source_date = '2026-08-27'
        
    scope = clean_text(row.get('Services legally indicated', ''))
    relevance = map_relevance(scope, org_type, country)
    
    website_url = ""
    signal = clean_text(row.get('Website signal', ''))
    web_status = map_website_status(signal)
    web_verif = map_website_verification(signal, country)
    
    email = clean_text(row.get('Email', ''))
    phone = clean_text(row.get('Phone', ''))
    city = clean_text(row.get('Location', ''))
    official_url = clean_text(row.get('Official record', ''))
    source_ds = map_source_dataset(country, regulator)
    
    priority = clean_text(row.get('Priority', 'Review'))
    confidence = "High" if priority in ['High', 'Medium'] else "Medium"
    next_action = map_next_action(country, priority)
    
    existing_rows.append({
        'Priority': priority,
        'Country': country,
        'Company name': c_name,
        'Organization type': org_type,
        'Regulator or professional body': regulator,
        'Licence / register number': licence_id,
        'Licence or registration status': lic_status,
        'Status checked date': checked_date if checked_date else '2026-08-28',
        'Source date': source_date,
        'Licence scope / permitted services': scope,
        'Recovery or disputes relevance': relevance,
        'Website URL': website_url,
        'Website status': web_status,
        'Website verification method': web_verif,
        'Email': email,
        'Phone': phone,
        'City / address': city,
        'Official source URL': official_url,
        'Source file or dataset': source_ds,
        'Confidence': confidence,
        'Next verification action': next_action
    })

print(f"Mapped {len(existing_rows)} existing rows to standard 21 columns.")

# Now write data to temporary intermediate pickle/csv to inspect
df_mapped = pd.DataFrame(existing_rows)
print("Breakdown of mapped countries:")
print(df_mapped['Country'].value_counts())
