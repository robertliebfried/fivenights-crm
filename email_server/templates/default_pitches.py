"""
Pre-built, high-converting cold email pitch templates tailored for licensed organizations
without a public website.
"""

DEFAULT_TEMPLATES = [
    {
        "name": "Legal Practice & Solicitors — Web Intake & Digital Credibility",
        "category": "Legal",
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
        "name": "Financial Advisers & Asset Managers — Trust & Investor Portal",
        "category": "Financial Advisory",
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
        "name": "Claims Management & Financial Disputes — Chargeback & Intake Calculator",
        "category": "Claims Management",
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
        "name": "Crypto & Blockchain Forensics — High-Tech Security Web Portal",
        "category": "Crypto / Forensics",
        "subject": "Modern website & forensic intake platform for {{company_name}}",
        "body_html": """<p>Dear {{company_name}} Team,</p>

<p>While analyzing regulated digital asset and investigation service entities registered under <strong>{{regulator}}</strong>, I noticed that {{company_name}} (Reg: <code>{{licence_number}}</code>) is actively authorized, yet lacks a dedicated public web portal.</p>

<p>In the blockchain forensics and digital asset industry, credibility is paramount. Victims of crypto fraud and institutional partners require an authoritative platform to submit transaction hashes (TXIDs), wallet addresses, and case parameters securely.</p>

<p>We build dark-mode and high-tech corporate websites tailored for blockchain intelligence:</p>
<ul>
  <li><strong>TXID & Wallet Intake Engine:</strong> Structured forms for receiving blockchain transaction data and chain IDs.</li>
  <li><strong>Institutional Credibility & Badges:</strong> Displaying your regulatory credentials under {{regulator}}.</li>
  <li><strong>Encrypted Client Communication:</strong> Secure contact workflows.</li>
</ul>

<p>Are you open to exploring a prototype web concept designed specifically for {{company_name}}?</p>

<p>Best regards,<br>
<strong>{{sender_name}}</strong><br>
{{sender_email}}</p>""",
        "body_text": """Dear {{company_name}} Team,

While analyzing digital asset and investigation entities registered under {{regulator}}, I noticed that {{company_name}} (Reg: {{licence_number}}) is actively listed, but currently lacks a dedicated public website.

In blockchain forensics and crypto investigations, an authoritative website allows clients and law firms to securely submit transaction hashes (TXIDs) and wallet data.

We build high-tech, responsive websites for blockchain analytics firms:
- Structured TXID & Wallet Address Intake Form
- Institutional Trust & Regulatory Display ({{regulator}})
- Encrypted Contact & Consultation Booking

Would you be open to reviewing a design prototype created for {{company_name}}?

Best regards,
{{sender_name}}
{{sender_email}}"""
    },
    {
        "name": "General Professional Services — Corporate Web Presence",
        "category": "General",
        "subject": "New website proposal for {{company_name}}",
        "body_html": """<p>Dear {{company_name}} Team,</p>

<p>I hope this email finds you well.</p>

<p>I am reaching out regarding {{company_name}}, listed in {{country}} under <strong>{{regulator}}</strong> (Reg: <code>{{licence_number}}</code>). We noticed that your company does not currently have a live corporate website.</p>

<p>We are a web development studio creating fast, high-converting, mobile-ready websites for licensed professional organizations. We handle domain registration, copywriting, responsive design, and contact form integration.</p>

<p>Would you have 5 minutes for a brief chat to see a sample mockup for {{company_name}}?</p>

<p>Best regards,<br>
<strong>{{sender_name}}</strong><br>
{{sender_email}}</p>""",
        "body_text": """Dear {{company_name}} Team,

I am reaching out regarding {{company_name}}, listed in {{country}} under {{regulator}} (Reg: {{licence_number}}). We noticed that your company does not currently have a live corporate website.

We create fast, high-converting, mobile-ready websites for licensed professional organizations. We handle everything from design to domain setup and lead capture forms.

Would you have 5 minutes for a brief chat to see a sample mockup for {{company_name}}?

Best regards,
{{sender_name}}
{{sender_email}}"""
    },
    {
        "name": "Inactive Clients — We Miss You & Major Updates",
        "category": "Re-engagement",
        "subject": "It's been a while, {{company_name}} — see what's new on {{site_name}}",
        "body_html": """<p>Hi {{company_name}},</p>

<p>We noticed that you haven't visited <strong>{{site_name}}</strong> in a while, and we wanted to personally reach out to check in.</p>

<p>Over the past few months, we've rolled out several major improvements designed to make your experience faster, smoother, and more rewarding:</p>
<ul>
  <li><strong>Enhanced Speed & Performance:</strong> Completely rebuilt infrastructure for instant loading and zero friction.</li>
  <li><strong>New Features & Expanded Options:</strong> Brand new capabilities requested directly by our community.</li>
  <li><strong>Priority Account Support:</strong> Dedicated assistance whenever you need help or have questions.</li>
</ul>

<p>Your account is still active and waiting for you. Come back and explore the latest updates today:</p>
<p style="margin: 20px 0;">
  <a href="https://{{site_name}}" style="background-color: #2563eb; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">Explore What's New &rarr;</a>
</p>

<p>If you need any assistance getting back into your account, simply reply directly to this email.</p>

<p>Warm regards,<br>
<strong>{{sender_name}}</strong><br>
Customer Success Team &bull; {{site_name}}<br>
{{sender_email}}</p>""",
        "body_text": """Hi {{company_name}},

We noticed that you haven't visited {{site_name}} in a while, and we wanted to personally check in.

Over the past few months, we've rolled out major upgrades:
- Faster infrastructure and smoother experience
- Brand new features and expanded options
- Direct priority support for your account

Your account is still active and waiting for you. Log back in to see what's new:
https://{{site_name}}

If you need any help or have forgotten your credentials, simply reply to this email!

Best regards,
{{sender_name}}
Customer Success Team • {{site_name}}
{{sender_email}}"""
    },
    {
        "name": "Inactive Clients — Exclusive Welcome-Back Bonus",
        "category": "Re-engagement",
        "subject": "Special welcome-back bonus for {{company_name}} on {{site_name}}",
        "body_html": """<p>Hello {{company_name}},</p>

<p>As a valued member of <strong>{{site_name}}</strong>, we wanted to extend a special welcome-back incentive to thank you for being part of our journey.</p>

<p>For the next 7 days, we have activated an exclusive welcome-back perk on your account:</p>
<div style="background-color: #f1f5f9; padding: 15px; border-left: 4px solid #2563eb; margin: 15px 0; border-radius: 4px;">
  <p style="margin: 0; font-weight: bold; color: #1e293b;">🎁 Exclusive VIP Re-activation Access</p>
  <p style="margin: 5px 0 0 0; color: #475569; font-size: 14px;">Instant priority queue, complimentary review, and personalized support on {{site_name}}.</p>
</div>

<p>You can claim this right now by logging into your profile:</p>
<p style="margin: 20px 0;">
  <a href="https://{{site_name}}" style="background-color: #10b981; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">Claim Your Welcome Perk &rarr;</a>
</p>

<p>We'd love to have you back with us!</p>

<p>Best regards,<br>
<strong>{{sender_name}}</strong><br>
{{site_name}} Support<br>
{{sender_email}}</p>""",
        "body_text": """Hello {{company_name}},

As a valued member of {{site_name}}, we wanted to extend an exclusive welcome-back incentive to welcome you back.

For the next 7 days, we have activated a special VIP Re-activation perk on your account, including priority access and personalized assistance.

Claim your perk and log back in here:
https://{{site_name}}

If you have any questions or feedback for us, just reply directly to this email.

Best regards,
{{sender_name}}
{{site_name}} Support
{{sender_email}}"""
    },
    {
        "name": "Inactive Clients — Quick Feedback & Account Check",
        "category": "Re-engagement",
        "subject": "Quick question regarding your account on {{site_name}}",
        "body_html": """<p>Hi {{company_name}},</p>

<p>I'm checking in from <strong>{{site_name}}</strong>. Our records show that you haven't logged in for some time, and I wanted to make sure everything was okay.</p>

<p>Did you run into any hurdles, or has what you were looking for changed?</p>

<p>If there is anything we can do to make {{site_name}} more useful for you, or if you'd like your account settings updated, could you let me know with a quick 1-line reply?</p>

<p>Either way, thank you for being with us!</p>

<p>Best regards,<br>
<strong>{{sender_name}}</strong><br>
{{sender_email}}</p>""",
        "body_text": """Hi {{company_name}},

I'm checking in from {{site_name}}. Our records show that you haven't logged in for some time, and I wanted to make sure everything was okay.

Did you run into any hurdles, or has what you were looking for changed?

If there is anything we can do to make {{site_name}} more useful for you, or if you'd like your account preferences updated, please let me know with a quick 1-line reply.

Thank you!

Best regards,
{{sender_name}}
{{sender_email}}"""
    }
]

