"""
Pre-built multi-step email drip sequences for high-converting outreach.
"""

DEFAULT_SEQUENCES = [
    {
        "name": "Legal Practices & Solicitors — 4-Step High-Trust Cadence",
        "description": "Tailored for Law Firms and Solicitors with court representation authority who lack a public website.",
        "steps": [
            {
                "step_number": 1,
                "delay_days": 0,
                "subject": "Digital presence & online client intake for {{company_name}}",
                "body_html": """<p>Dear {{company_name}} Team,</p>

<p>I noticed while reviewing the official directory for <strong>{{regulator}}</strong> in {{country}} that {{company_name}} (Reg: <code>{{licence_number}}</code>) is actively authorized, yet does not currently maintain a public website.</p>

<p>In high-stakes legal disputes and financial claims, prospective clients overwhelmingly verify credentials online before reaching out. Without a dedicated web portal, many prospective clients hesitate or turn to competitor firms with visible web presences.</p>

<p>We build streamlined, high-trust digital web platforms specifically for regulated legal practices. Key features we implement:</p>
<ul>
  <li><strong>Instant Case Evaluation & Intake Forms:</strong> Securely capture initial case facts, claim amounts, and client documents.</li>
  <li><strong>Official Registry Verification Badge:</strong> Display verified regulatory standing ({{regulator}}) to build immediate trust.</li>
  <li><strong>Confidential Client Booking:</strong> Integrated scheduling for initial consultation calls.</li>
  <li><strong>Full GDPR & Compliance Disclaimers:</strong> Standard legal disclosures and secure SSL encryption.</li>
</ul>

<p>Would you be open to a quick 5-minute call or a brief 3-page interactive prototype tailored for <strong>{{company_name}}</strong>?</p>

<p>Best regards,<br>
<strong>{{sender_name}}</strong><br>
Web Development & Digital Presence Specialist<br>
{{sender_email}}</p>""",
                "body_text": """Dear {{company_name}} Team,

I noticed while reviewing the official register of {{regulator}} in {{country}} that {{company_name}} (Licence/Reg: {{licence_number}}) is actively listed, but does not currently have an active public website.

In legal practice and dispute resolution, prospective clients verify credentials online before reaching out. Without a dedicated website, many potential clients hesitate to initiate contact.

We build modern, compliant websites tailored for regulated legal and advisory firms:
- Secure Client Intake & Claim Evaluation Forms
- Verified Regulatory Standing Badges ({{regulator}})
- Automated Consultation Scheduling
- Full GDPR & Compliance Disclaimers

Would you be open to seeing a brief interactive demo tailored for {{company_name}}?

Best regards,
{{sender_name}}
{{sender_email}}"""
            },
            {
                "step_number": 2,
                "delay_days": 3,
                "subject": "Re: Digital presence for {{company_name}} (Quick example)",
                "body_html": """<p>Hi {{company_name}} Team,</p>

<p>Following up on my note from a few days ago regarding establishing a dedicated web presence for <strong>{{company_name}}</strong> under <strong>{{regulator}}</strong>.</p>

<p>We recently built a minimalist client-intake website for a regulated practice that increased their qualified consultation inquiries by over 40% in the first month—simply by giving claimants a secure, mobile-friendly way to upload dispute evidence directly.</p>

<p>I would love to send you a quick 2-minute video walkthrough of what a modern intake portal would look like for {{company_name}}.</p>

<p>Are you available for a brief chat this Thursday or Friday?</p>

<p>Best regards,<br>
<strong>{{sender_name}}</strong><br>
{{sender_email}}</p>""",
                "body_text": """Hi {{company_name}} Team,

Following up on my note from a few days ago regarding establishing a dedicated web presence for {{company_name}} under {{regulator}}.

We recently built a minimalist client-intake website for a regulated practice that increased their qualified consultation inquiries by over 40% in the first month—simply by giving claimants a secure, mobile-friendly way to submit details online.

I would love to send you a quick 2-minute video walkthrough of what a modern intake portal would look like for {{company_name}}.

Are you available for a brief chat this Thursday or Friday?

Best regards,
{{sender_name}}
{{sender_email}}"""
            },
            {
                "step_number": 3,
                "delay_days": 4,
                "subject": "Case Intake Demo mockup for {{company_name}}",
                "body_html": """<p>Dear {{company_name}},</p>

<p>I put together a quick initial layout concept for <strong>{{company_name}}</strong> featuring:</p>
<ol>
  <li>Your official regulatory credentials badge ({{regulator}} - Ref: {{licence_number}}).</li>
  <li>A secure, encrypted preliminary case evaluation form.</li>
  <li>Direct one-click phone and email contact buttons for mobile clients in {{city}}.</li>
</ol>

<p>There is zero obligation—I would just like to get your thoughts on the design concept.</p>

<p>Could I email you the preview link?</p>

<p>Warm regards,<br>
<strong>{{sender_name}}</strong><br>
{{sender_email}}</p>""",
                "body_text": """Dear {{company_name}},

I put together a quick initial layout concept for {{company_name}} featuring:
1. Your official regulatory credentials badge ({{regulator}} - Ref: {{licence_number}}).
2. A secure, encrypted preliminary case evaluation form.
3. Direct one-click phone and email contact buttons for mobile clients in {{city}}.

There is zero obligation—I would just like to get your thoughts on the design concept.

Could I email you the preview link?

Warm regards,
{{sender_name}}
{{sender_email}}"""
            },
            {
                "step_number": 4,
                "delay_days": 5,
                "subject": "Closing the loop — Website for {{company_name}}",
                "body_html": """<p>Hi {{company_name}} Team,</p>

<p>I understand you are likely busy managing active client cases and regulatory matters.</p>

<p>I won't follow up further, but if you decide you would like to establish a professional, compliant website for <strong>{{company_name}}</strong> in the future, please feel free to reach out anytime.</p>

<p>Wishing you continued success in your practice.</p>

<p>Best regards,<br>
<strong>{{sender_name}}</strong><br>
{{sender_email}}</p>""",
                "body_text": """Hi {{company_name}} Team,

I understand you are likely busy managing active client cases and regulatory matters.

I won't follow up further, but if you decide you would like to establish a professional, compliant website for {{company_name}} in the future, please feel free to reach out anytime.

Wishing you continued success in your practice.

Best regards,
{{sender_name}}
{{sender_email}}"""
            }
        ]
    },
    {
        "name": "Financial Advisers & Asset Managers — 3-Step Trust Cadence",
        "description": "Designed for investment advisers, CIFs, EAFs, and wealth managers without a public website.",
        "steps": [
            {
                "step_number": 1,
                "delay_days": 0,
                "subject": "Website development & investor trust portal for {{company_name}}",
                "body_html": """<p>Hello {{company_name}} Team,</p>

<p>While cross-referencing regulated financial institutions under <strong>{{regulator}}</strong>, I saw that {{company_name}} is registered for financial advisory services in {{country}} (Ref: <code>{{licence_number}}</code>), but does not have an active public website registered.</p>

<p>In today's wealth and financial advisory landscape, having a professional, responsive web portal is the single most important factor for investor confidence and regulatory transparency.</p>

<p>We specialize in building clean, minimalist websites for independent financial firms:</p>
<ul>
  <li><strong>Regulatory Credibility:</strong> Clear presentation of your permitted scope and {{regulator}} oversight.</li>
  <li><strong>Client Onboarding & Appointment Scheduler:</strong> Direct calendar booking for qualified prospects.</li>
  <li><strong>Responsive Mobile-First Design:</strong> Fast, accessible on all devices with custom typography.</li>
  <li><strong>Compliant Financial Disclaimers:</strong> Risk warnings and privacy disclosures in full compliance with local regulations.</li>
</ul>

<p>I would be delighted to send over a customized preview design for <strong>{{company_name}}</strong>. Could we connect briefly this week?</p>

<p>Warm regards,<br>
<strong>{{sender_name}}</strong><br>
{{sender_email}}</p>""",
                "body_text": """Hello {{company_name}} Team,

While cross-referencing regulated institutions under {{regulator}}, I saw that {{company_name}} is registered for advisory services in {{country}} (Ref: {{licence_number}}), but does not have an active website registered.

A professional, modern website is crucial for establishing investor trust and streamlining client acquisition.

We build clean, compliant websites for regulated financial firms:
- Professional presentation of regulatory credentials ({{regulator}})
- Online appointment scheduling & intake
- Mobile-responsive layout and secure hosting
- Full regulatory disclaimer & privacy compliance

Can I send over a quick draft mockup designed for {{company_name}}?

Warm regards,
{{sender_name}}
{{sender_email}}"""
            },
            {
                "step_number": 2,
                "delay_days": 3,
                "subject": "Quick question regarding {{company_name}} digital presence",
                "body_html": """<p>Hi {{company_name}} Team,</p>

<p>I wanted to quickly check in regarding my previous message about creating a high-trust web portal for <strong>{{company_name}}</strong>.</p>

<p>Many advisory firms we work with rely on their site not just for new leads, but to provide existing institutional partners with a clear, compliant overview of their authorized services under {{regulator}}.</p>

<p>We handle everything turn-key: domain setup, responsive layouts, compliance copywriting, and secure hosting.</p>

<p>Would 10 minutes next Tuesday work for a brief call?</p>

<p>Best regards,<br>
<strong>{{sender_name}}</strong><br>
{{sender_email}}</p>""",
                "body_text": """Hi {{company_name}} Team,

I wanted to quickly check in regarding my previous message about creating a high-trust web portal for {{company_name}}.

Many advisory firms we work with rely on their site not just for new leads, but to provide existing institutional partners with a clear, compliant overview of their authorized services under {{regulator}}.

We handle everything turn-key: domain setup, responsive layouts, compliance copywriting, and secure hosting.

Would 10 minutes next Tuesday work for a brief call?

Best regards,
{{sender_name}}
{{sender_email}}"""
            },
            {
                "step_number": 3,
                "delay_days": 4,
                "subject": "Final check-in: Web development for {{company_name}}",
                "body_html": """<p>Hi {{company_name}},</p>

<p>I assume timing might not be ideal right now, so I will pause my outreach.</p>

<p>If building a modern digital presence for {{company_name}} becomes a priority down the line, I'd be happy to share our portfolio and assist.</p>

<p>Wishing you all the best,</p>

<p><strong>{{sender_name}}</strong><br>
{{sender_email}}</p>""",
                "body_text": """Hi {{company_name}},

I assume timing might not be ideal right now, so I will pause my outreach.

If building a modern digital presence for {{company_name}} becomes a priority down the line, I'd be happy to share our portfolio and assist.

Wishing you all the best,

{{sender_name}}
{{sender_email}}"""
            }
        ]
    },
    {
        "name": "Claims Management & Financial Disputes — 3-Step Cadence",
        "description": "Optimized for regulated claims management companies and dispute specialists.",
        "steps": [
            {
                "step_number": 1,
                "delay_days": 0,
                "subject": "Custom website & claim intake calculator for {{company_name}}",
                "body_html": """<p>Dear {{company_name}},</p>

<p>I came across {{company_name}} in the official records for <strong>{{regulator}}</strong> in {{country}} (Reg: <code>{{licence_number}}</code>). I noted that your practice focuses on claims handling and dispute resolution, but does not currently feature a dedicated website.</p>

<p>For dispute and transaction recovery services, an automated intake portal is essential. It allows prospective claimants to calculate estimated eligibility and submit documentation 24/7 without manual staff overhead.</p>

<p>We can build a modern web presence for {{company_name}} including:</p>
<ul>
  <li><strong>Interactive Claim Eligibility Calculator:</strong> Allows claimants to calculate dispute timelines and requirements.</li>
  <li><strong>Secure Document Upload:</strong> Safe intake of banking statements and dispute transaction receipts.</li>
  <li><strong>Live Verification Widget:</strong> Direct confirmation of your authorization under {{regulator}}.</li>
</ul>

<p>Let me know if you would like to review a quick 1-minute live demo of how this would look for {{company_name}}.</p>

<p>Best regards,<br>
<strong>{{sender_name}}</strong><br>
{{sender_email}}</p>""",
                "body_text": """Dear {{company_name}},

I came across {{company_name}} in the official records for {{regulator}} in {{country}} (Reg: {{licence_number}}). I noted your focus on claims and dispute resolution, but saw you don't have an active website.

For dispute and claims resolution, a dedicated intake website allows clients to check eligibility and submit claims 24/7.

We build custom web solutions for claims and dispute firms:
- Interactive Claim Eligibility Calculator
- Secure Client Document & Evidence Upload Portal
- Regulatory Standing Display ({{regulator}})
- Automated Lead Qualification

Would you be interested in a 1-minute live demo tailored for {{company_name}}?

Best regards,
{{sender_name}}
{{sender_email}}"""
            },
            {
                "step_number": 2,
                "delay_days": 4,
                "subject": "Automating claim submissions for {{company_name}}",
                "body_html": """<p>Hi {{company_name}} Team,</p>

<p>Just checking back on my note regarding an automated intake portal for {{company_name}}.</p>

<p>Having an automated eligibility questionnaire pre-qualifies dispute inquiries before your team spends time on calls, saving hours of manual review each week.</p>

<p>I'd love to share a sample interactive form tailored to your regulatory scope under {{regulator}}.</p>

<p>Would you have 5 minutes for a quick look?</p>

<p>Best regards,<br>
<strong>{{sender_name}}</strong><br>
{{sender_email}}</p>""",
                "body_text": """Hi {{company_name}} Team,

Just checking back on my note regarding an automated intake portal for {{company_name}}.

Having an automated eligibility questionnaire pre-qualifies dispute inquiries before your team spends time on calls, saving hours of manual review each week.

I'd love to share a sample interactive form tailored to your regulatory scope under {{regulator}}.

Would you have 5 minutes for a quick look?

Best regards,
{{sender_name}}
{{sender_email}}"""
            },
            {
                "step_number": 3,
                "delay_days": 4,
                "subject": "Final note re: Claims intake portal for {{company_name}}",
                "body_html": """<p>Hi {{company_name}},</p>

<p>I'll leave it here in case this isn't a current focus for your team.</p>

<p>Should you look to launch a modern intake site for your claims services in {{country}} later this year, feel free to keep my details handy.</p>

<p>Best regards,<br>
<strong>{{sender_name}}</strong><br>
{{sender_email}}</p>""",
                "body_text": """Hi {{company_name}},

I'll leave it here in case this isn't a current focus for your team.

Should you look to launch a modern intake site for your claims services in {{country}} later this year, feel free to keep my details handy.

Best regards,
{{sender_name}}
{{sender_email}}"""
            }
        ]
    },
    {
        "name": "Inactive Client Win-Back & Re-activation (3-Step Cadence)",
        "description": "Multi-step automated sequence designed specifically to re-engage past clients who have not visited or used your sites for a long time.",
        "steps": [
            {
                "step_number": 1,
                "delay_days": 0,
                "subject": "It's been a while, {{company_name}} — see what's new on {{site_name}}",
                "body_html": """<p>Hi {{company_name}},</p>

<p>We noticed you haven't logged into <strong>{{site_name}}</strong> for a while, and we wanted to personally reach out to check in.</p>

<p>Over the past few months, we've implemented major upgrades:</p>
<ul>
  <li><strong>Instant Speed:</strong> Re-engineered performance for quick response and zero delays.</li>
  <li><strong>Expanded Capabilities:</strong> New options and streamlined tools.</li>
  <li><strong>VIP Support:</strong> Direct priority assistance for your account.</li>
</ul>

<p>Your account is ready and waiting for you. Log back in to explore the improvements:</p>
<p style="margin: 20px 0;">
  <a href="https://{{site_name}}" style="background-color: #2563eb; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">Return to {{site_name}} &rarr;</a>
</p>

<p>Warm regards,<br>
<strong>{{sender_name}}</strong><br>
{{sender_email}}</p>""",
                "body_text": """Hi {{company_name}},

We noticed you haven't logged into {{site_name}} for a while, and wanted to personally check in.

We've rolled out major upgrades:
- Faster infrastructure and smoother experience
- Expanded tools and features
- Direct priority support

Your account is ready. Log back in to see what's new:
https://{{site_name}}

Best regards,
{{sender_name}}
{{sender_email}}"""
            },
            {
                "step_number": 2,
                "delay_days": 3,
                "subject": "Exclusive welcome-back perk waiting for {{company_name}}",
                "body_html": """<p>Hello {{company_name}},</p>

<p>Following up on my message from a few days ago regarding <strong>{{site_name}}</strong>.</p>

<p>We've reserved a special welcome-back incentive on your profile for the next 7 days, including priority access and personalized assistance.</p>

<p>You can claim this right now when you access your account:</p>
<p style="margin: 20px 0;">
  <a href="https://{{site_name}}" style="background-color: #10b981; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">Access Your Account &rarr;</a>
</p>

<p>Best regards,<br>
<strong>{{sender_name}}</strong><br>
{{site_name}} Team<br>
{{sender_email}}</p>""",
                "body_text": """Hello {{company_name}},

Following up on my note regarding {{site_name}}.

We've reserved an exclusive welcome-back perk on your profile for the next 7 days, including priority access and personalized assistance.

Claim it here:
https://{{site_name}}

Best regards,
{{sender_name}}
{{site_name}} Team
{{sender_email}}"""
            },
            {
                "step_number": 3,
                "delay_days": 5,
                "subject": "Quick question regarding your account on {{site_name}}",
                "body_html": """<p>Hi {{company_name}},</p>

<p>Final quick check-in from our team. If your requirements have changed or you ran into any issues with <strong>{{site_name}}</strong>, we'd appreciate any quick feedback so we can improve.</p>

<p>Simply reply to this email with any questions or thoughts.</p>

<p>Thank you for being part of {{site_name}}!</p>

<p>Best regards,<br>
<strong>{{sender_name}}</strong><br>
{{sender_email}}</p>""",
                "body_text": """Hi {{company_name}},

Final quick check-in. If your requirements have changed or you ran into any issues with {{site_name}}, we'd love any feedback so we can improve.

Just hit reply to let us know.

Thank you!

Best regards,
{{sender_name}}
{{sender_email}}"""
            }
        ]
    }
]
