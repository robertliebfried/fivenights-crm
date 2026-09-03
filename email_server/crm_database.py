import aiosqlite
import json
from datetime import datetime
from email_server.config import DB_PATH, DEFAULT_SETTINGS
from email_server.templates.default_sequences import DEFAULT_SEQUENCES

async def get_db():
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db

async def init_crm_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA journal_mode=WAL;")
        
        # 1. Pipeline Stages
        await db.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_stages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                order_index INTEGER NOT NULL,
                color TEXT NOT NULL DEFAULT '#2563eb'
            );
        """)
        
        # Insert default pipeline stages if empty
        async with db.execute("SELECT COUNT(*) FROM pipeline_stages") as c:
            count = (await c.fetchone())[0]
            if count == 0:
                default_stages = [
                    (1, "New Prospect", 1, "#3b82f6"),
                    (2, "Outreach Planned", 2, "#6366f1"),
                    (3, "Contacted / Sequence", 3, "#8b5cf6"),
                    (4, "Interested / Meeting", 4, "#f59e0b"),
                    (5, "Proposal / Mockup Sent", 5, "#06b6d4"),
                    (6, "Won / Closed Deal", 6, "#10b981"),
                    (7, "Lost / Inactive", 7, "#64748b")
                ]
                await db.executemany("""
                    INSERT INTO pipeline_stages (id, name, order_index, color)
                    VALUES (?, ?, ?, ?)
                """, default_stages)

        # 2. CRM Contacts Table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                contact_person TEXT DEFAULT '',
                email TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                country TEXT DEFAULT '',
                city TEXT DEFAULT '',
                regulator TEXT DEFAULT '',
                licence_number TEXT DEFAULT '',
                relevance TEXT DEFAULT '',
                organization_type TEXT DEFAULT '',
                website_status TEXT DEFAULT '',
                stage_id INTEGER DEFAULT 1,
                deal_value REAL DEFAULT 0.0,
                notes TEXT DEFAULT '',
                tags TEXT DEFAULT '',
                assigned_agent_id INTEGER DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (stage_id) REFERENCES pipeline_stages(id),
                FOREIGN KEY (assigned_agent_id) REFERENCES agents(id)
            );
        """)

        try:
            await db.execute("ALTER TABLE contacts ADD COLUMN assigned_agent_id INTEGER DEFAULT NULL")
        except Exception:
            pass

        # 3. Sequences Table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sequences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                status TEXT NOT NULL DEFAULT 'paused', -- active, paused, draft
                mailbox_id INTEGER DEFAULT 1,
                schedule_days TEXT DEFAULT '["Mon", "Tue", "Wed", "Thu", "Fri"]',
                schedule_start_hour INTEGER DEFAULT 9,
                schedule_end_hour INTEGER DEFAULT 18,
                stop_on_reply BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 4. Sequence Steps Table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sequence_steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sequence_id INTEGER NOT NULL,
                step_number INTEGER NOT NULL,
                delay_days INTEGER NOT NULL DEFAULT 0,
                subject TEXT NOT NULL,
                body_html TEXT NOT NULL,
                body_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sequence_id) REFERENCES sequences(id) ON DELETE CASCADE
            );
        """)

        # Populate default sequences if empty
        async with db.execute("SELECT COUNT(*) FROM sequences") as c:
            seq_count = (await c.fetchone())[0]
            if seq_count == 0:
                for seq in DEFAULT_SEQUENCES:
                    cursor = await db.execute("""
                        INSERT INTO sequences (name, description, status)
                        VALUES (?, ?, 'paused')
                    """, (seq["name"], seq["description"]))
                    seq_id = cursor.lastrowid
                    for st in seq["steps"]:
                        await db.execute("""
                            INSERT INTO sequence_steps (sequence_id, step_number, delay_days, subject, body_html, body_text)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (seq_id, st["step_number"], st["delay_days"], st["subject"], st["body_html"], st["body_text"]))

        # 5. Sequence Enrollments
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sequence_enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sequence_id INTEGER NOT NULL,
                contact_id INTEGER NOT NULL,
                current_step INTEGER NOT NULL DEFAULT 1,
                status TEXT NOT NULL DEFAULT 'paused', -- active, paused, completed, replied, bounced
                next_send_at TIMESTAMP,
                last_sent_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sequence_id) REFERENCES sequences(id) ON DELETE CASCADE,
                FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
            );
        """)

        # 6. Contact Notes & Activity Timeline
        await db.execute("""
            CREATE TABLE IF NOT EXISTS contact_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER NOT NULL,
                author TEXT DEFAULT 'You',
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
            );
        """)

        # 7. Multi-Mailbox Accounts (Google Workspace & Custom SMTP)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS mailboxes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                smtp_host TEXT NOT NULL DEFAULT 'smtp.gmail.com',
                smtp_port INTEGER NOT NULL DEFAULT 587,
                smtp_user TEXT DEFAULT '',
                smtp_password TEXT DEFAULT '',
                smtp_use_tls BOOLEAN DEFAULT 1,
                smtp_use_ssl BOOLEAN DEFAULT 0,
                sender_name TEXT NOT NULL,
                sender_email TEXT NOT NULL,
                daily_limit INTEGER DEFAULT 100,
                sent_today INTEGER DEFAULT 0,
                assigned_agent_id INTEGER DEFAULT NULL,
                provider TEXT DEFAULT 'google_workspace',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Migrations for existing mailboxes table
        try:
            await db.execute("ALTER TABLE mailboxes ADD COLUMN assigned_agent_id INTEGER DEFAULT NULL")
        except Exception:
            pass
        try:
            await db.execute("ALTER TABLE mailboxes ADD COLUMN provider TEXT DEFAULT 'google_workspace'")
        except Exception:
            pass

        # Seed 5 Mailbox slots if less than 5 exist
        async with db.execute("SELECT COUNT(*) FROM mailboxes") as c:
            mb_count = (await c.fetchone())[0]
            if mb_count == 0:
                # First mailbox with default settings
                await db.execute("""
                    INSERT INTO mailboxes (
                        id, name, smtp_host, smtp_port, smtp_user, smtp_password,
                        smtp_use_tls, smtp_use_ssl, sender_name, sender_email, daily_limit, is_active
                    ) VALUES (
                        1, 'Domain 1 (Primary)', :smtp_host, :smtp_port, :smtp_user,
                        :smtp_password, :smtp_use_tls, :smtp_use_ssl, :sender_name,
                        :sender_email, :daily_limit, 1
                    )
                """, DEFAULT_SETTINGS)
                mb_count = 1

            for i in range(mb_count + 1, 6):
                await db.execute("""
                    INSERT INTO mailboxes (
                        id, name, smtp_host, smtp_port, smtp_user, smtp_password,
                        smtp_use_tls, smtp_use_ssl, sender_name, sender_email, daily_limit, is_active
                    ) VALUES (
                        ?, ?, 'smtp.yourdomain.com', 587, '', '', 1, 0, ?, '', 50, 0
                    )
                """, (
                    i,
                    f"Domain {i}",
                    f"Team Domain {i}"
                ))

        # 8. Agents / Team Members Table (Max, Fred, Chriss)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                role TEXT NOT NULL DEFAULT 'Outreach Specialist',
                avatar_color TEXT NOT NULL DEFAULT '#2563eb',
                signature TEXT DEFAULT '',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Seed John (Admin), Max, Fred, and Chriss
        default_agents = [
            (1, "John", "john@fivenights.fun", "System Administrator & Managing Director", "#ef4444", "Best regards,\nJohn\nAdministrator • FiveNights.fun\njohn@fivenights.fun"),
            (2, "Max", "max@fivenights.fun", "Senior Outreach & Lead Account Executive", "#3b82f6", "Best regards,\nMax\nOutreach Specialist • FiveNights.fun\nmax@fivenights.fun"),
            (3, "Fred", "fred@fivenights.fun", "Client Relations & Win-Back Manager", "#10b981", "Best regards,\nFred\nClient Success Manager • FiveNights.fun\nfred@fivenights.fun"),
            (4, "Chriss", "chriss@fivenights.fun", "Portfolio & Account Specialist", "#8b5cf6", "Best regards,\nChriss\nAccount Specialist • FiveNights.fun\nchriss@fivenights.fun")
        ]
        for ag in default_agents:
            await db.execute("""
                INSERT OR REPLACE INTO agents (id, name, email, role, avatar_color, signature, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """, ag)

        await db.commit()

# CRM Contact CRUD Operations
async def get_crm_stages_with_counts():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT s.*, 
                   COUNT(c.id) as contact_count,
                   COALESCE(SUM(c.deal_value), 0.0) as total_deal_value
            FROM pipeline_stages s
            LEFT JOIN contacts c ON s.id = c.stage_id
            GROUP BY s.id
            ORDER BY s.order_index ASC
        """) as cursor:
            return [dict(r) for r in await cursor.fetchall()]

async def get_crm_contacts(stage_id=None, query=None, country=None, page=1, page_size=50):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        where_clauses = []
        params = []
        
        if stage_id:
            where_clauses.append("c.stage_id = ?")
            params.append(stage_id)
        if country and country != 'All':
            where_clauses.append("c.country = ?")
            params.append(country)
        if query:
            where_clauses.append("(c.company_name LIKE ? OR c.email LIKE ? OR c.contact_person LIKE ? OR c.city LIKE ? OR c.regulator LIKE ?)")
            q = f"%{query}%"
            params.extend([q, q, q, q, q])
            
        where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        # Count total
        count_sql = f"SELECT COUNT(*) FROM contacts c {where_sql}"
        async with db.execute(count_sql, params) as c:
            total_count = (await c.fetchone())[0]
            
        # Get page items
        data_sql = f"""
            SELECT c.*, s.name as stage_name, s.color as stage_color
            FROM contacts c
            LEFT JOIN pipeline_stages s ON c.stage_id = s.id
            {where_sql}
            ORDER BY c.updated_at DESC
            LIMIT ? OFFSET ?
        """
        offset = (page - 1) * page_size
        params.extend([page_size, offset])
        async with db.execute(data_sql, params) as cursor:
            items = [dict(r) for r in await cursor.fetchall()]
            
        return {
            "total": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size if total_count > 0 else 1,
            "items": items
        }

async def get_crm_contact_by_id(contact_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT c.*, s.name as stage_name, s.color as stage_color
            FROM contacts c
            LEFT JOIN pipeline_stages s ON c.stage_id = s.id
            WHERE c.id = ?
        """, (contact_id,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                return None
            contact = dict(row)
            
            # Fetch notes
            async with db.execute("SELECT * FROM contact_notes WHERE contact_id = ? ORDER BY id DESC", (contact_id,)) as nc:
                contact['notes_list'] = [dict(r) for r in await nc.fetchall()]
                
            # Fetch enrollments
            async with db.execute("""
                SELECT e.*, sq.name as sequence_name
                FROM sequence_enrollments e
                LEFT JOIN sequences sq ON e.sequence_id = sq.id
                WHERE e.contact_id = ?
            """, (contact_id,)) as ec:
                contact['enrollments'] = [dict(r) for r in await ec.fetchall()]
                
            return contact

async def update_contact_stage(contact_id: int, new_stage_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE contacts 
            SET stage_id = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, (new_stage_id, contact_id))
        await db.commit()

async def add_contact_note(contact_id: int, content: str, author: str = "You"):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO contact_notes (contact_id, author, content)
            VALUES (?, ?, ?)
        """, (contact_id, author, content))
        await db.execute("UPDATE contacts SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (contact_id,))
        await db.commit()

async def import_leads_to_crm(leads: list, target_stage_id: int = 1):
    async with aiosqlite.connect(DB_PATH) as db:
        imported_count = 0
        for l in leads:
            # Check if email/company already exists in contacts
            email = l.get('email', '').strip()
            company = l.get('company_name', '').strip()
            
            async with db.execute(
                "SELECT id FROM contacts WHERE company_name = ? OR (email != '' AND email = ?)",
                (company, email)
            ) as c:
                exists = await c.fetchone()
                if not exists:
                    await db.execute("""
                        INSERT INTO contacts (
                            company_name, email, phone, country, city, regulator,
                            licence_number, relevance, organization_type, website_status,
                            stage_id, deal_value, notes, tags
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0.0, '', ?)
                    """, (
                        company, email, l.get('phone', ''), l.get('country', ''),
                        l.get('city', ''), l.get('regulator', ''), l.get('licence_number', ''),
                        l.get('relevance', ''), l.get('organization_type', ''),
                        l.get('website_status', ''), target_stage_id,
                        l.get('relevance', '')
                    ))
                    imported_count += 1
        await db.commit()
        return imported_count

# Sequence Management
async def get_all_sequences_with_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT sq.*,
                   COUNT(DISTINCT st.id) as total_steps,
                   COUNT(DISTINCT e.id) as total_enrolled,
                   COUNT(DISTINCT CASE WHEN e.status = 'active' THEN e.id END) as active_enrolled,
                   COUNT(DISTINCT CASE WHEN e.status = 'completed' THEN e.id END) as completed_enrolled,
                   COUNT(DISTINCT CASE WHEN e.status = 'replied' THEN e.id END) as replied_enrolled
            FROM sequences sq
            LEFT JOIN sequence_steps st ON sq.id = st.sequence_id
            LEFT JOIN sequence_enrollments e ON sq.id = e.sequence_id
            GROUP BY sq.id
            ORDER BY sq.id ASC
        """) as cursor:
            return [dict(r) for r in await cursor.fetchall()]

async def get_sequence_detail(sequence_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM sequences WHERE id = ?", (sequence_id,)) as c:
            row = await c.fetchone()
            if not row:
                return None
            seq = dict(row)
            
            # Fetch steps
            async with db.execute("SELECT * FROM sequence_steps WHERE sequence_id = ? ORDER BY step_number ASC", (sequence_id,)) as sc:
                seq['steps'] = [dict(r) for r in await sc.fetchall()]
                
            # Fetch enrollments
            async with db.execute("""
                SELECT e.*, c.company_name, c.email, c.country, c.regulator, s.name as stage_name
                FROM sequence_enrollments e
                LEFT JOIN contacts c ON e.contact_id = c.id
                LEFT JOIN pipeline_stages s ON c.stage_id = s.id
                WHERE e.sequence_id = ?
                ORDER BY e.id DESC
                LIMIT 100
            """, (sequence_id,)) as ec:
                seq['enrollments'] = [dict(r) for r in await ec.fetchall()]
                
            return seq

async def enroll_contacts_in_sequence(sequence_id: int, contact_ids: list):
    async with aiosqlite.connect(DB_PATH) as db:
        enrolled = 0
        for cid in contact_ids:
            # Check if already enrolled in this sequence
            async with db.execute(
                "SELECT id FROM sequence_enrollments WHERE sequence_id = ? AND contact_id = ?",
                (sequence_id, cid)
            ) as c:
                exists = await c.fetchone()
                if not exists:
                    # Enrolled safely in paused status by default
                    await db.execute("""
                        INSERT INTO sequence_enrollments (
                            sequence_id, contact_id, current_step, status, next_send_at
                        ) VALUES (?, ?, 1, 'paused', CURRENT_TIMESTAMP)
                    """, (sequence_id, cid))
                    enrolled += 1
            await db.commit()
        return enrolled

# ==========================================
# 5-Domain Multi-Mailbox CRUD Operations
# ==========================================
async def get_all_mailboxes(agent_id: int = None):
    """Retrieve mailboxes with agent assignment and usage stats"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        sql = """
            SELECT m.id, m.name, m.smtp_host, m.smtp_port, m.smtp_user, 
                   CASE WHEN m.smtp_password IS NOT NULL AND m.smtp_password != '' THEN 1 ELSE 0 END as has_password,
                   m.smtp_use_tls, m.smtp_use_ssl, m.sender_name, m.sender_email,
                   m.daily_limit, m.sent_today, m.assigned_agent_id, m.provider,
                   m.is_active, m.created_at,
                   a.name as assigned_agent_name, a.role as assigned_agent_role, a.avatar_color as assigned_agent_color
            FROM mailboxes m
            LEFT JOIN agents a ON m.assigned_agent_id = a.id
        """
        params = []
        if agent_id:
            sql += " WHERE m.assigned_agent_id = ? OR m.assigned_agent_id IS NULL"
            params.append(agent_id)
        sql += " ORDER BY m.id ASC"

        async with db.execute(sql, params) as cursor:
            return [dict(r) for r in await cursor.fetchall()]

async def get_mailbox_by_id(mailbox_id: int, include_password: bool = False):
    """Retrieve a specific mailbox by ID"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT m.*, a.name as assigned_agent_name 
            FROM mailboxes m 
            LEFT JOIN agents a ON m.assigned_agent_id = a.id 
            WHERE m.id = ?
        """, (mailbox_id,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                return None
            res = dict(row)
            if not include_password:
                res["has_password"] = bool(res.get("smtp_password"))
                res["smtp_password"] = ""
            return res

async def save_mailbox(data: dict):
    """Create or update a mailbox configuration for Google Workspace or custom SMTP"""
    mailbox_id = data.get("id")
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        # Check if exists
        existing = None
        if mailbox_id:
            async with db.execute("SELECT * FROM mailboxes WHERE id = ?", (mailbox_id,)) as c:
                existing = await c.fetchone()

        # Handle password preservation if blank submitted
        password = data.get("smtp_password", "")
        if not password and existing and existing["smtp_password"]:
            password = existing["smtp_password"]

        raw_agent = data.get("assigned_agent_id")
        if raw_agent in ("", "none", 0, "0", None):
            assigned_agent_id = None
        else:
            try:
                assigned_agent_id = int(raw_agent)
            except (ValueError, TypeError):
                assigned_agent_id = None

        provider = data.get("provider", "google_workspace")

        if existing:
            await db.execute("""
                UPDATE mailboxes SET
                    name = ?, smtp_host = ?, smtp_port = ?, smtp_user = ?,
                    smtp_password = ?, smtp_use_tls = ?, smtp_use_ssl = ?,
                    sender_name = ?, sender_email = ?, daily_limit = ?,
                    assigned_agent_id = ?, provider = ?, is_active = ?
                WHERE id = ?
            """, (
                data.get("name", existing["name"]),
                data.get("smtp_host", existing["smtp_host"]),
                int(data.get("smtp_port", 587)),
                data.get("smtp_user", ""),
                password,
                1 if data.get("smtp_use_tls", True) else 0,
                1 if data.get("smtp_use_ssl", False) else 0,
                data.get("sender_name", existing["sender_name"]),
                data.get("sender_email", existing["sender_email"]),
                int(data.get("daily_limit", 100)),
                assigned_agent_id,
                provider,
                1 if data.get("is_active", True) else 0,
                mailbox_id
            ))
            await db.commit()
            return mailbox_id
        else:
            cursor = await db.execute("""
                INSERT INTO mailboxes (
                    name, smtp_host, smtp_port, smtp_user, smtp_password,
                    smtp_use_tls, smtp_use_ssl, sender_name, sender_email,
                    daily_limit, sent_today, assigned_agent_id, provider, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?)
            """, (
                data.get("name", "Google Workspace Account"),
                data.get("smtp_host", "smtp.gmail.com"),
                int(data.get("smtp_port", 587)),
                data.get("smtp_user", ""),
                password,
                1 if data.get("smtp_use_tls", True) else 0,
                1 if data.get("smtp_use_ssl", False) else 0,
                data.get("sender_name", ""),
                data.get("sender_email", ""),
                int(data.get("daily_limit", 100)),
                assigned_agent_id,
                provider,
                1 if data.get("is_active", True) else 0
            ))
            await db.commit()
            return cursor.lastrowid

async def delete_mailbox(mailbox_id: int):
    """Delete a mailbox (if not one of the primary 5) or reset it"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM mailboxes WHERE id = ?", (mailbox_id,))
        await db.commit()
        return True

async def increment_mailbox_sent(mailbox_id: int):
    """Increment sent_today count for a mailbox"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE mailboxes SET sent_today = sent_today + 1 WHERE id = ?
        """, (mailbox_id,))
        await db.commit()

async def reset_all_mailboxes_daily():
    """Reset daily sent counters for all mailboxes (e.g. at midnight)"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE mailboxes SET sent_today = 0")
        await db.commit()

# ==========================================
# Inactive Client Re-engagement Import
# ==========================================
async def import_reengagement_clients(clients: list, default_site: str = "fivenights.fun"):
    """Import inactive clients for win-back outreach"""
    async with aiosqlite.connect(DB_PATH) as db:
        imported = 0
        updated = 0
        for c in clients:
            email = c.get("email", "").strip()
            if not email:
                continue
            name = c.get("name", "") or c.get("company_name", "") or email.split("@")[0].capitalize()
            site = c.get("site_name", "") or default_site
            last_active = c.get("last_active", "several months ago")
            notes = f"Inactive client from {site}. Last active: {last_active}"
            tags = f"reengagement,inactive_client,{site}"

            async with db.execute("SELECT id FROM contacts WHERE email = ?", (email,)) as cur:
                existing = await cur.fetchone()

            if existing:
                await db.execute("""
                    UPDATE contacts 
                    SET company_name = COALESCE(NULLIF(company_name, ''), ?),
                        tags = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (name, tags, notes, existing[0]))
                updated += 1
            else:
                await db.execute("""
                    INSERT INTO contacts (
                        company_name, email, relevance, stage_id, notes, tags
                    ) VALUES (?, ?, 'Inactive Client', 1, ?, ?)
                """, (name, email, notes, tags))
                imported += 1
        await db.commit()
        return {"imported": imported, "updated": updated, "total": imported + updated}

# ==========================================
# Agent Accounts CRUD Operations (Max, Fred, Chriss)
# ==========================================
async def get_all_agents():
    """Retrieve all team agents"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM agents ORDER BY id ASC") as cursor:
            return [dict(r) for r in await cursor.fetchall()]

async def get_agent_by_id(agent_id: int):
    """Retrieve a single agent by ID"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM agents WHERE id = ?", (agent_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def save_agent(data: dict):
    """Create or update an agent account"""
    agent_id = data.get("id")
    async with aiosqlite.connect(DB_PATH) as db:
        if agent_id:
            await db.execute("""
                UPDATE agents SET
                    name = ?, email = ?, role = ?, avatar_color = ?,
                    signature = ?, is_active = ?
                WHERE id = ?
            """, (
                data.get("name"),
                data.get("email"),
                data.get("role", "Outreach Specialist"),
                data.get("avatar_color", "#2563eb"),
                data.get("signature", ""),
                1 if data.get("is_active", True) else 0,
                agent_id
            ))
            await db.commit()
            return agent_id
        else:
            cursor = await db.execute("""
                INSERT INTO agents (name, email, role, avatar_color, signature, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                data.get("name"),
                data.get("email"),
                data.get("role", "Outreach Specialist"),
                data.get("avatar_color", "#2563eb"),
                data.get("signature", ""),
                1 if data.get("is_active", True) else 0
            ))
            await db.commit()
            return cursor.lastrowid

async def delete_agent(agent_id: int):
    """Delete an agent account"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM agents WHERE id = ?", (agent_id,))
        await db.commit()
        return True

async def import_contacts_from_csv_list(contacts: list, default_tags: str = "csv_import", assigned_agent_id: int = None):
    """Bulk import parsed CSV contacts with deduplication and agent assignment"""
    imported = 0
    updated = 0
    async with aiosqlite.connect(DB_PATH) as db:
        for c in contacts:
            email = (c.get("email") or "").strip()
            if not email or "@" not in email:
                continue

            name = (c.get("name") or c.get("contact_person") or "").strip()
            company = (c.get("company") or c.get("company_name") or name or "Client").strip()
            phone = (c.get("phone") or "").strip()
            country = (c.get("country") or "").strip()
            city = (c.get("city") or "").strip()
            notes = (c.get("notes") or "").strip()
            tags = (c.get("tags") or default_tags or "csv_import").strip()
            agent_id = c.get("assigned_agent_id") or assigned_agent_id

            async with db.execute("SELECT id FROM contacts WHERE email = ?", (email,)) as cur:
                existing = await cur.fetchone()

            if existing:
                await db.execute("""
                    UPDATE contacts SET
                        company_name = COALESCE(NULLIF(?, ''), company_name),
                        contact_person = COALESCE(NULLIF(?, ''), contact_person),
                        phone = COALESCE(NULLIF(?, ''), phone),
                        country = COALESCE(NULLIF(?, ''), country),
                        tags = ?,
                        assigned_agent_id = COALESCE(?, assigned_agent_id),
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (company, name, phone, country, tags, agent_id, existing[0]))
                updated += 1
            else:
                await db.execute("""
                    INSERT INTO contacts (
                        company_name, contact_person, email, phone, country, city,
                        stage_id, notes, tags, assigned_agent_id
                    ) VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, ?)
                """, (company, name, email, phone, country, city, notes, tags, agent_id))
                imported += 1

        await db.commit()
        return {"imported": imported, "updated": updated, "total": imported + updated}



