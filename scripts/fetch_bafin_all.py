import sys
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

print("Fetching BaFin institutions...")
base_url = 'https://portal.mvp.bafin.de/database/InstInfo/sucheForm.do'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

bafin_records = []

# Fetch pages from kategorieId=50 (Finanzdienstleistungsinstitute / Wertpapierinstitute)
# and kategorieId=60 (Kapitalverwaltungsgesellschaften)
categories = [
    ('50', 'Finanzdienstleistungsinstitut / Wertpapierinstitut', 12),
    ('60', 'Kapitalverwaltungsgesellschaft', 4),
    ('70', 'Kreditdienstleistungsinstitut', 3)
]

for cat_id, cat_name, max_pages in categories:
    print(f"Querying BaFin category {cat_id} ({cat_name})...")
    for page in range(1, max_pages + 1):
        params = {
            'kategorieId': cat_id,
            'sucheButtonInstitut': 'Suche'
        }
        if page > 1:
            params['d-4012550-p'] = str(page)
            
        try:
            r = requests.get(base_url, params=params, headers=headers, timeout=15)
            if r.status_code != 200:
                print(f"Page {page} status {r.status_code}")
                break
            soup = BeautifulSoup(r.text, 'html.parser')
            table = soup.find('table')
            if not table:
                print(f"No table on page {page}")
                break
            rows = table.find_all('tr')[1:] # skip header
            if not rows:
                break
            
            for tr in rows:
                tds = tr.find_all('td')
                if len(tds) < 2:
                    continue
                name = tds[0].text.strip()
                a_tag = tds[0].find('a')
                detail_url = ""
                inst_id = ""
                if a_tag and a_tag.get('href'):
                    href = a_tag.get('href')
                    detail_url = f"https://portal.mvp.bafin.de/database/InstInfo/{href}"
                    if 'institutId=' in href:
                        inst_id = href.split('institutId=')[1].split('&')[0]
                
                gattung = tds[1].text.strip()
                ombudsman = tds[2].text.strip() if len(tds) > 2 else ""
                
                # Determine scope & relevance
                g_lower = gattung.lower()
                if 'krypto' in g_lower:
                    scope = "Kryptowertedienstleistungen / Krypto-Verwahrgeschäft (WpIG/KWG)"
                    relevance = "Crypto-asset services authorization"
                    prio = "High"
                elif 'kreditdienst' in g_lower or 'factoring' in g_lower or 'leasing' in g_lower:
                    scope = f"Kreditdienstleistungen / Factoring / Finanzdienstleistungen ({gattung})"
                    relevance = "General financial authorization; recovery authority not established"
                    prio = "Medium"
                elif 'wertpapier' in g_lower or 'anlage' in g_lower:
                    scope = f"Wertpapierdienstleistungen / Anlageberatung / Finanzportfolioverwaltung ({gattung})"
                    relevance = "Financial or investment advice authorization"
                    prio = "High"
                else:
                    scope = f"BaFin Erlaubnis ({gattung})"
                    relevance = "General financial authorization; recovery authority not established"
                    prio = "Medium"
                
                licence_no = f"BaFin ID {inst_id}" if inst_id else "Not published in list view"
                
                bafin_records.append({
                    'Priority': prio,
                    'Country': 'Germany',
                    'Company name': name,
                    'Organization type': gattung if gattung else cat_name,
                    'Regulator or professional body': 'Federal Financial Supervisory Authority (BaFin) / Bundesanstalt für Finanzdienstleistungsaufsicht',
                    'Licence / register number': licence_no,
                    'Licence or registration status': 'Current / Authorised (BaFin Unternehmensdatenbank)',
                    'Status checked date': '2026-08-28',
                    'Source date': '2026',
                    'Licence scope / permitted services': scope,
                    'Recovery or disputes relevance': relevance,
                    'Website URL': '',
                    'Website status': 'Not provided in source — verify manually',
                    'Website verification method': 'BaFin institutional registry extract (website not recorded in basic database view)',
                    'Email': '',
                    'Phone': '',
                    'City / address': ombudsman if ombudsman else 'Germany',
                    'Official source URL': detail_url if detail_url else 'https://portal.mvp.bafin.de/database/InstInfo/',
                    'Source file or dataset': 'BaFin Unternehmensdatenbank (Instituts-Info)',
                    'Confidence': 'High',
                    'Next verification action': f'Verify BaFin registered domain and commercial register (Handelsregister) entry for {name}'
                })
            
            time.sleep(0.5)
        except Exception as e:
            print(f"Error on cat {cat_id} page {page}: {e}")
            break

print(f"Fetched {len(bafin_records)} records from BaFin.")
df_bafin = pd.DataFrame(bafin_records)
df_bafin.to_pickle('scripts/bafin_leads.pkl')
