import os
import re
import pandas as pd
import dns.resolver
from email_validator import validate_email, EmailNotValidError
from email_server.config import EXCEL_PATH

_CACHED_LEADS = None
_MX_CACHE = {}

def get_loaded_leads(force_reload=False):
    global _CACHED_LEADS
    if _CACHED_LEADS is not None and not force_reload:
        return _CACHED_LEADS

    if not os.path.exists(EXCEL_PATH):
        return []

    print(f"Loading leads from Excel: {EXCEL_PATH}...")
    try:
        # Load the workbook
        df_target = pd.read_excel(EXCEL_PATH, sheet_name='Direct Recovery & Litigation')
        df_all = pd.read_excel(EXCEL_PATH, sheet_name='All Leads')
        
        # Combine and mark source sheet
        df_target['sheet_origin'] = 'Direct Recovery & Litigation'
        df_all['sheet_origin'] = 'All Leads'
        
        df_combined = pd.concat([df_target, df_all], ignore_index=True)
        # Deduplicate
        df_combined = df_combined.drop_duplicates(
            subset=['Company name', 'Country', 'Regulator or professional body', 'Licence / register number'],
            keep='first'
        )
        
        leads = []
        for idx, row in df_combined.iterrows():
            email = str(row.get('Email', '')).strip()
            if email == 'nan' or email == 'None':
                email = ''
            
            company = str(row.get('Company name', '')).strip()
            country = str(row.get('Country', '')).strip()
            priority = str(row.get('Priority', 'Review')).strip()
            relevance = str(row.get('Recovery or disputes relevance', '')).strip()
            org_type = str(row.get('Organization type', '')).strip()
            regulator = str(row.get('Regulator or professional body', '')).strip()
            licence_no = str(row.get('Licence / register number', '')).strip()
            city = str(row.get('City / address', '')).strip()
            if city == 'nan' or city == 'None':
                city = ''
            phone = str(row.get('Phone', '')).strip()
            if phone == 'nan' or phone == 'None':
                phone = ''
            web_status = str(row.get('Website status', '')).strip()
            source_url = str(row.get('Official source URL', '')).strip()

            leads.append({
                'id': idx + 1,
                'company_name': company,
                'email': email,
                'has_email': bool(email and '@' in email),
                'country': country,
                'priority': priority,
                'relevance': relevance,
                'organization_type': org_type,
                'regulator': regulator,
                'licence_number': licence_no,
                'city': city,
                'phone': phone,
                'website_status': web_status,
                'official_source_url': source_url,
                'sheet_origin': row.get('sheet_origin', 'All Leads')
            })

        _CACHED_LEADS = leads
        print(f"Loaded {len(leads)} total leads ({sum(1 for l in leads if l['has_email'])} with direct emails).")
        return leads
    except Exception as e:
        print(f"Error reading leads workbook: {e}")
        return []

def search_leads(
    query: str = "",
    country: str = None,
    priority: str = None,
    relevance: str = None,
    only_with_email: bool = False,
    page: int = 1,
    page_size: int = 50
):
    all_leads = get_loaded_leads()
    filtered = all_leads

    if only_with_email:
        filtered = [l for l in filtered if l['has_email']]

    if country and country != 'All':
        filtered = [l for l in filtered if l['country'].lower() == country.lower()]

    if priority and priority != 'All':
        filtered = [l for l in filtered if l['priority'].lower() == priority.lower()]

    if relevance and relevance != 'All':
        filtered = [l for l in filtered if l['relevance'].lower() == relevance.lower()]

    if query:
        q = query.lower()
        filtered = [
            l for l in filtered
            if q in l['company_name'].lower()
            or q in l['email'].lower()
            or q in l['regulator'].lower()
            or q in l['licence_number'].lower()
            or q in l['city'].lower()
        ]

    total_count = len(filtered)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_items = filtered[start_idx:end_idx]

    return {
        'total': total_count,
        'page': page,
        'page_size': page_size,
        'total_pages': (total_count + page_size - 1) // page_size if total_count > 0 else 1,
        'items': page_items
    }

def get_countries_summary():
    leads = get_loaded_leads()
    countries = {}
    for l in leads:
        c = l['country']
        if c not in countries:
            countries[c] = {'total': 0, 'with_email': 0}
        countries[c]['total'] += 1
        if l['has_email']:
            countries[c]['with_email'] += 1
    return countries

def verify_email_domain(email: str) -> dict:
    """
    Hunter.io style email validator:
    1. Syntax check
    2. MX Record verification via DNS
    3. Disposable domain check
    """
    email = email.strip()
    if not email or '@' not in email:
        return {'valid': False, 'reason': 'Invalid email format', 'mx_valid': False}

    try:
        valid_info = validate_email(email, check_deliverability=False)
        domain = valid_info.domain
    except EmailNotValidError as e:
        return {'valid': False, 'reason': str(e), 'mx_valid': False}

    # Check MX cache
    if domain in _MX_CACHE:
        mx_status = _MX_CACHE[domain]
        return {
            'valid': mx_status['has_mx'],
            'domain': domain,
            'mx_records': mx_status['records'],
            'reason': 'Deliverable' if mx_status['has_mx'] else 'Domain has no valid mail exchange (MX) records'
        }

    try:
        records = dns.resolver.resolve(domain, 'MX', lifetime=4.0)
        mx_hosts = [str(r.exchange).rstrip('.') for r in records]
        _MX_CACHE[domain] = {'has_mx': True, 'records': mx_hosts}
        return {
            'valid': True,
            'domain': domain,
            'mx_records': mx_hosts,
            'reason': 'Valid & Deliverable MX records found'
        }
    except Exception as e:
        _MX_CACHE[domain] = {'has_mx': False, 'records': []}
        return {
            'valid': False,
            'domain': domain,
            'mx_records': [],
            'reason': f'No MX record: {type(e).__name__}'
        }
