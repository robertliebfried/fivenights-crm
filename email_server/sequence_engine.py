import asyncio
import datetime
import random
from email_server.database import get_db, get_settings, log_email_action
from email_server.crm_database import get_crm_contact_by_id, update_contact_stage
from email_server.email_service import render_email_content, send_single_email

_SEQUENCE_WORKER_TASK = None
_WORKER_RUNNING = False

async def sequence_scheduler_loop():
    """Continuous background worker that checks and advances active sequence enrollments"""
    global _WORKER_RUNNING
    _WORKER_RUNNING = True
    print("Sequence Scheduler Worker started (in safe monitoring mode)...")

    while _WORKER_RUNNING:
        try:
            db = await get_db()
            settings = await get_settings()
            is_dry_run = bool(settings.get("dry_run_mode", True))

            # Query ready active enrollments
            # An enrollment is ready if:
            # 1. sequence status is 'active'
            # 2. enrollment status is 'active'
            # 3. next_send_at <= CURRENT_TIMESTAMP
            async with db.execute("""
                SELECT e.*, sq.name as sequence_name, sq.stop_on_reply,
                       c.company_name, c.email, c.country, c.city, c.regulator,
                       c.licence_number, c.relevance, c.organization_type, c.stage_id
                FROM sequence_enrollments e
                JOIN sequences sq ON e.sequence_id = sq.id
                JOIN contacts c ON e.contact_id = c.id
                WHERE sq.status = 'active'
                  AND e.status = 'active'
                  AND (e.next_send_at IS NULL OR e.next_send_at <= CURRENT_TIMESTAMP)
                  AND c.email != ''
                LIMIT 5
            """) as cursor:
                ready_enrollments = [dict(r) for r in await cursor.fetchall()]

            for item in ready_enrollments:
                enrollment_id = item['id']
                seq_id = item['sequence_id']
                contact_id = item['contact_id']
                current_step_num = item['current_step']

                # Fetch current step definition
                async with db.execute("""
                    SELECT * FROM sequence_steps 
                    WHERE sequence_id = ? AND step_number = ?
                """, (seq_id, current_step_num)) as sc:
                    step = await sc.fetchone()

                if not step:
                    # No more steps -> mark sequence completed for this contact
                    await db.execute("""
                        UPDATE sequence_enrollments 
                        SET status = 'completed', updated_at = CURRENT_TIMESTAMP 
                        WHERE id = ?
                    """, (enrollment_id,))
                    await db.commit()
                    continue

                step_data = dict(step)
                to_email = item['email'].strip()
                company_name = item['company_name']

                # Render subject and body with contact data
                subject = render_email_content(step_data['subject'], item, settings)
                body_html = render_email_content(step_data['body_html'], item, settings)
                body_text = render_email_content(step_data['body_text'], item, settings)

                # Send or Dry-run simulation
                res = await send_single_email(to_email, subject, body_html, body_text, settings)

                if res.get("success"):
                    status_code = "DRY_RUN_SUCCESS" if is_dry_run else "SENT"
                    
                    # Check for next step in sequence
                    async with db.execute("""
                        SELECT * FROM sequence_steps 
                        WHERE sequence_id = ? AND step_number = ?
                    """, (seq_id, current_step_num + 1)) as next_sc:
                        next_step = await next_sc.fetchone()

                    if next_step:
                        next_delay_days = dict(next_step).get('delay_days', 3)
                        # In dry-run mode advance quickly for simulation, in live mode wait actual days
                        if is_dry_run:
                            next_send = (datetime.datetime.now() + datetime.timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
                        else:
                            next_send = (datetime.datetime.now() + datetime.timedelta(days=next_delay_days)).strftime('%Y-%m-%d %H:%M:%S')

                        await db.execute("""
                            UPDATE sequence_enrollments 
                            SET current_step = current_step + 1,
                                last_sent_at = CURRENT_TIMESTAMP,
                                next_send_at = ?,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE id = ?
                        """, (next_send, enrollment_id))
                    else:
                        await db.execute("""
                            UPDATE sequence_enrollments 
                            SET status = 'completed',
                                last_sent_at = CURRENT_TIMESTAMP,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE id = ?
                        """, (enrollment_id,))

                    # Update contact stage in CRM to 'Contacted / Sequence' (Stage 3) if in stage 1 or 2
                    if item['stage_id'] in [1, 2]:
                        await db.execute("""
                            UPDATE contacts SET stage_id = 3, updated_at = CURRENT_TIMESTAMP WHERE id = ?
                        """, (contact_id,))

                    # Record log
                    await log_email_action(
                        campaign_id=seq_id,
                        recipient=to_email,
                        company_name=company_name,
                        subject=f"[Step {current_step_num}] {subject}",
                        status=status_code,
                        error_details=f"Sequence: {item['sequence_name']}",
                        is_dry_run=is_dry_run
                    )
                else:
                    err_msg = res.get("error", "Dispatch failed")
                    await db.execute("""
                        UPDATE sequence_enrollments 
                        SET status = 'failed', updated_at = CURRENT_TIMESTAMP 
                        WHERE id = ?
                    """, (enrollment_id,))
                    await log_email_action(
                        campaign_id=seq_id,
                        recipient=to_email,
                        company_name=company_name,
                        subject=f"[Step {current_step_num}] {subject}",
                        status="FAILED",
                        error_details=err_msg,
                        is_dry_run=is_dry_run
                    )

                await db.commit()
                # Anti-spam interval
                await asyncio.sleep(2.0 if is_dry_run else 15.0)

            await db.close()
        except Exception as e:
            print(f"Error in sequence scheduler loop: {e}")

        # Poll interval
        await asyncio.sleep(10)

def start_sequence_scheduler():
    global _SEQUENCE_WORKER_TASK
    if _SEQUENCE_WORKER_TASK is None or _SEQUENCE_WORKER_TASK.done():
        _SEQUENCE_WORKER_TASK = asyncio.create_task(sequence_scheduler_loop())

def stop_sequence_scheduler():
    global _WORKER_RUNNING, _SEQUENCE_WORKER_TASK
    _WORKER_RUNNING = False
    if _SEQUENCE_WORKER_TASK:
        _SEQUENCE_WORKER_TASK.cancel()
        _SEQUENCE_WORKER_TASK = None
