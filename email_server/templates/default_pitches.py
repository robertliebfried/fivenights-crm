"""
B2C email templates for FiveNights customer retention and VIP management.
"""

DEFAULT_TEMPLATES = [
    {
        "name": "VIP Concierge - Personal Account Manager Introduction",
        "category": "VIP Retention",
        "subject": "Exclusive VIP privileges for {{contact_person}}",
        "body_html": "<p>Hi {{contact_person}},</p><p>My name is <strong>{{sender_name}}</strong>, your dedicated VIP Account Manager at FiveNights. Your account now includes exclusive benefits: direct concierge access, bespoke weekly perks and reloads, express priority processing, and exclusive early access to new features.</p><p>Is there anything I can set up for you today?</p><p>Warm regards,<br><strong>{{sender_name}}</strong><br>VIP Client Manager - FiveNights<br>{{sender_email}}</p>",
        "body_text": "Hi {{contact_person}},\n\nI am your dedicated VIP Account Manager at FiveNights.\n\nYour account includes:\n- Direct concierge access\n- Weekly perks and reload bonuses\n- Express priority processing\n- Exclusive early access\n\nIs there anything I can set up for you today?\n\nWarm regards,\n{{sender_name}}\nVIP Client Manager - FiveNights\n{{sender_email}}"
    },
    {
        "name": "Customer Win-Back - Exclusive Welcome Back Perk",
        "category": "Re-activation",
        "subject": "We miss you, {{contact_person}} - a return perk is waiting",
        "body_html": "<p>Hello {{contact_person}},</p><p>It has been a while since your last visit to FiveNights. Your welcome-back rewards are ready: exclusive re-activation bonus, instant match on next deposit, and zero delay priority support.</p><p><a href='https://fivenights.fun'>Return to FiveNights and Claim Perk</a></p><p>Best regards,<br><strong>{{sender_name}}</strong><br>Customer Success - FiveNights<br>{{sender_email}}</p>",
        "body_text": "Hello {{contact_person}},\n\nIt has been a while since your last visit and we wanted to check in!\n\nYour exclusive return reward is waiting:\n- Special Welcome-Back Bonus\n- Instant Match on next deposit\n- Priority support\n\nLog in at https://fivenights.fun to claim your perk.\n\nBest regards,\n{{sender_name}}\nCustomer Success - FiveNights\n{{sender_email}}"
    },
    {
        "name": "VIP Tier Upgrade - Loyalty Celebration",
        "category": "Loyalty",
        "subject": "Congratulations {{contact_person}}! Your VIP Tier Upgrade is now active",
        "body_html": "<p>Dear {{contact_person}},</p><p>Congratulations! Your account has been upgraded to <strong>VIP Gold Status</strong>. Your new privileges: higher limits and faster withdrawals, weekly cashback and customized gifts, personal account concierge.</p><p>Your VIP Upgrade Celebration Reward is already active on your profile.</p><p>Sincerely,<br><strong>{{sender_name}}</strong><br>VIP Relations Director - FiveNights<br>{{sender_email}}</p>",
        "body_text": "Dear {{contact_person}},\n\nYour FiveNights account has been upgraded to VIP Gold Status!\n\nYour new privileges:\n- Priority limits and expedited withdrawals\n- Weekly cashback and personalized perks\n- Direct personal account concierge\n\nSincerely,\n{{sender_name}}\nVIP Relations - FiveNights\n{{sender_email}}"
    },
    {
        "name": "1-on-1 Check-In - Personal Customer Feedback",
        "category": "Customer Care",
        "subject": "Quick question about your FiveNights experience, {{contact_person}}",
        "body_html": "<p>Hi {{contact_person}},</p><p>I am reaching out directly to see how everything has been going with your account recently. Could you take 30 seconds to share any quick feedback or requests? I am right here if you need anything.</p><p>Cheers,<br><strong>{{sender_name}}</strong><br>{{sender_email}}</p>",
        "body_text": "Hi {{contact_person}},\n\nI am reaching out to see how your FiveNights experience has been.\n\nCould you share any quick feedback in 30 seconds?\n\nCheers,\n{{sender_name}}\n{{sender_email}}"
    }
]
