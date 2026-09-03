import aiosqlite
import json
from datetime import datetime
from email_server.config import DB_PATH, DEFAULT_SETTINGS
from email_server.templates.default_pitches import DEFAULT_TEMPLATES

async def get_db():
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA journal_mode=WAL;")
        
        # 1. Settings table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                smtp_host TEXT NOT NULL,
                smtp_port INTEGER NOT NULL,
                smtp_user TEXT,
                smtp_password TEXT,
                smtp_use_tls BOOLEAN NOT NULL DEFAULT 1,
                smtp_use_ssl BOOLEAN NOT NULL DEFAULT 0,
                sender_name TEXT NOT NULL,
                sender_email TEXT NOT NULL,
                reply_to TEXT,
                daily_limit INTEGER NOT NULL DEFAULT 50,
                delay_min INTEGER NOT NULL DEFAULT 10,
                delay_max INTEGER NOT NULL DEFAULT 25,
                dry_run_mode BOOLEAN NOT NULL DEFAULT 1,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Insert default settings if empty
        async with db.execute("SELECT COUNT(*) FROM settings WHERE id = 1") as cursor:
            count = (await cursor.fetchone())[0]
            if count == 0:
                await db.execute("""
                    INSERT INTO settings (
                        id, smtp_host, smtp_port, smtp_user, smtp_password,
                        smtp_use_tls, smtp_use_ssl, sender_name, sender_email,
                        reply_to, daily_limit, delay_min, delay_max, dry_run_mode
                    ) VALUES (
                        1, :smtp_host, :smtp_port, :smtp_user, :smtp_password,
                        :smtp_use_tls, :smtp_use_ssl, :sender_name, :sender_email,
                        :reply_to, :daily_limit, :delay_min, :delay_max, :dry_run_mode
                    )
                """, DEFAULT_SETTINGS)

        # 2. Templates table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                subject TEXT NOT NULL,
                body_html TEXT NOT NULL,
                body_text TEXT NOT NULL,
                is_default BOOLEAN NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Populate default templates if empty
        async with db.execute("SELECT COUNT(*) FROM templates") as cursor:
            tmpl_count = (await cursor.fetchone())[0]
            if tmpl_count == 0:
                for tmpl in DEFAULT_TEMPLATES:
                    await db.execute("""
                        INSERT INTO templates (name, category, subject, body_html, body_text, is_default)
                        VALUES (?, ?, ?, ?, ?, 1)
                    """, (tmpl["name"], tmpl["category"], tmpl["subject"], tmpl["body_html"], tmpl["body_text"]))

        # 3. Campaigns table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                template_id INTEGER,
                custom_subject TEXT,
                custom_body_html TEXT,
                custom_body_text TEXT,
                status TEXT NOT NULL DEFAULT 'draft', -- draft, running, paused, completed, cancelled
                total_leads INTEGER NOT NULL DEFAULT 0,
                sent_count INTEGER NOT NULL DEFAULT 0,
                failed_count INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (template_id) REFERENCES templates(id)
            );
        """)

        # 4. Campaign Leads table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS campaign_leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER NOT NULL,
                email TEXT NOT NULL,
                company_name TEXT NOT NULL,
                country TEXT,
                organization_type TEXT,
                regulator TEXT,
                licence_number TEXT,
                city TEXT,
                relevance TEXT,
                status TEXT NOT NULL DEFAULT 'pending', -- pending, sent, failed, skipped
                error_msg TEXT,
                sent_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
            );
        """)

        # 5. Activity Logs table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS email_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER,
                recipient_email TEXT NOT NULL,
                company_name TEXT,
                subject TEXT,
                status TEXT NOT NULL, -- SENT, FAILED, DRY_RUN_SUCCESS, SKIPPED
                error_details TEXT,
                is_dry_run BOOLEAN NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        await db.commit()

async def get_settings():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM settings WHERE id = 1") as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return DEFAULT_SETTINGS

async def update_settings(data: dict):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE settings SET
                smtp_host = :smtp_host,
                smtp_port = :smtp_port,
                smtp_user = :smtp_user,
                smtp_password = :smtp_password,
                smtp_use_tls = :smtp_use_tls,
                smtp_use_ssl = :smtp_use_ssl,
                sender_name = :sender_name,
                sender_email = :sender_email,
                reply_to = :reply_to,
                daily_limit = :daily_limit,
                delay_min = :delay_min,
                delay_max = :delay_max,
                dry_run_mode = :dry_run_mode,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = 1
        """, data)
        await db.commit()
    return await get_settings()

async def get_all_templates():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM templates ORDER BY is_default DESC, id ASC") as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

async def get_template_by_id(template_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM templates WHERE id = ?", (template_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def create_template(name: str, category: str, subject: str, body_html: str, body_text: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO templates (name, category, subject, body_html, body_text, is_default)
            VALUES (?, ?, ?, ?, ?, 0)
        """, (name, category, subject, body_html, body_text))
        await db.commit()
        return cursor.lastrowid

async def get_all_campaigns():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT c.*, t.name as template_name 
            FROM campaigns c 
            LEFT JOIN templates t ON c.template_id = t.id 
            ORDER BY c.id DESC
        """) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

async def get_campaign_by_id(campaign_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT c.*, t.name as template_name 
            FROM campaigns c 
            LEFT JOIN templates t ON c.template_id = t.id 
            WHERE c.id = ?
        """, (campaign_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def get_campaign_leads(campaign_id: int, status: str = None, limit: int = 200):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        query = "SELECT * FROM campaign_leads WHERE campaign_id = ?"
        params = [campaign_id]
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY id ASC LIMIT ?"
        params.append(limit)
        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

async def create_campaign(name: str, template_id: int, custom_subject: str, custom_body_html: str, custom_body_text: str, leads: list):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO campaigns (name, template_id, custom_subject, custom_body_html, custom_body_text, status, total_leads)
            VALUES (?, ?, ?, ?, ?, 'draft', ?)
        """, (name, template_id, custom_subject, custom_body_html, custom_body_text, len(leads)))
        campaign_id = cursor.lastrowid
        
        for lead in leads:
            await db.execute("""
                INSERT INTO campaign_leads (
                    campaign_id, email, company_name, country, organization_type,
                    regulator, licence_number, city, relevance, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
            """, (
                campaign_id,
                lead.get('email', ''),
                lead.get('company_name', ''),
                lead.get('country', ''),
                lead.get('organization_type', ''),
                lead.get('regulator', ''),
                lead.get('licence_number', ''),
                lead.get('city', ''),
                lead.get('relevance', '')
            ))
            
        await db.commit()
        return campaign_id

async def log_email_action(campaign_id, recipient, company_name, subject, status, error_details="", is_dry_run=False):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO email_logs (campaign_id, recipient_email, company_name, subject, status, error_details, is_dry_run)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (campaign_id, recipient, company_name, subject, status, error_details, 1 if is_dry_run else 0))
        await db.commit()

async def get_recent_logs(limit: int = 100):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM email_logs ORDER BY id DESC LIMIT ?", (limit,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

async def get_system_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        stats = {}
        async with db.execute("SELECT COUNT(*) FROM email_logs WHERE status = 'SENT'") as c:
            stats['total_sent_real'] = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM email_logs WHERE status = 'DRY_RUN_SUCCESS'") as c:
            stats['total_dry_run'] = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM email_logs WHERE status LIKE '%FAIL%'") as c:
            stats['total_failed'] = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM campaigns") as c:
            stats['total_campaigns'] = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM campaign_leads WHERE status = 'pending'") as c:
            stats['total_pending_leads'] = (await c.fetchone())[0]
        return stats
