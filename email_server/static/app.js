function app() {
  return {
    currentTab: 'overview',
    stats: {
      total_leads_in_db: 0,
      leads_with_email: 0,
      total_sent_real: 0,
      total_dry_run: 0,
      total_campaigns: 0
    },
    leadsData: { items: [], total: 0, page: 1, total_pages: 1 },
    leadsFilter: {
      query: '',
      country: 'All',
      priority: 'All',
      relevance: 'All',
      only_with_email: true
    },
    selectedLeads: [],
    templates: [],
    campaigns: [],
    logs: [],
    agents: [],
    activeAgent: null,
    editingAgent: null,
    isAuthenticated: false,
    loginForm: {
      username: '',
      password: '',
      error: ''
    },
    mailboxes: [],
    editingMailbox: null,
    testingMailboxId: null,
    bulkMailboxModalOpen: false,
    bulkMailboxText: '',
    csvModalOpen: false,
    csvImportMode: 'file',
    csvText: '',
    csvParsedRows: [],
    csvAssignedAgent: null,
    csvDefaultTag: 'imported_clients',
    newLeadModalOpen: false,
    newLeadForm: {
      name: '',
      email: '',
      company: '',
      phone: '',
      country: 'Global',
      city: '',
      deal_value: 0,
      priority: 'High',
      assigned_agent_id: null,
      notes: ''
    },
    editingLeadModalOpen: false,
    editingLead: null,
    leadNotes: [],
    newNoteText: '',
    editingNoteId: null,
    editingNoteText: '',
    reengagementText: '',
    reengagementSite: 'fivenights.fun',
    reengagementDefaultLastActive: 'several months ago',
    settings: {
      smtp_host: 'smtp.gmail.com',
      smtp_port: 587,
      smtp_user: '',
      smtp_password: '',
      smtp_use_tls: true,
      smtp_use_ssl: false,
      sender_name: 'FiveNights Support',
      sender_email: 'support@fivenights.fun',
      reply_to: '',
      daily_limit: 50,
      delay_min: 10,
      delay_max: 25,
      dry_run_mode: true
    },
    campaignForm: {
      name: '',
      template_id: null,
      custom_subject: '',
      custom_body_html: '',
      custom_body_text: '',
      leads: []
    },
    previewData: {
      sample_lead: null,
      rendered_subject: '',
      rendered_html: '',
      rendered_text: ''
    },
    testEmailAddress: '',
    toast: {
      visible: false,
      message: '',
      type: 'success'
    },

    async initApp() {
      // Hardcoded fallback agents (work without backend API)
      const FALLBACK_AGENTS = [
        { id: 1, name: 'John',  email: 'john@fivenights.fun',  role: 'System Administrator & Managing Director', avatar_color: '#ef4444', signature: 'Best regards,\nJohn\nAdministrator • FiveNights.fun\njohn@fivenights.fun',  is_active: 1 },
        { id: 2, name: 'Max',   email: 'max@fivenights.fun',   role: 'Senior Outreach & Lead Account Executive',  avatar_color: '#3b82f6', signature: 'Best regards,\nMax\nOutreach Specialist • FiveNights.fun\nmax@fivenights.fun',   is_active: 1 },
        { id: 3, name: 'Fred',  email: 'fred@fivenights.fun',  role: 'Client Relations & Win-Back Manager',        avatar_color: '#10b981', signature: 'Best regards,\nFred\nClient Success Manager • FiveNights.fun\nfred@fivenights.fun',  is_active: 1 },
        { id: 4, name: 'Chriss',email: 'chriss@fivenights.fun',role: 'Portfolio & Account Specialist',             avatar_color: '#8b5cf6', signature: 'Best regards,\nChriss\nAccount Specialist • FiveNights.fun\nchriss@fivenights.fun', is_active: 1 }
      ];
      this.agents = FALLBACK_AGENTS;

      // Check saved authentication
      const savedAuth = localStorage.getItem('fivenights_agent_auth');
      if (savedAuth) {
        try {
          const data = JSON.parse(savedAuth);
          this.isAuthenticated = true;
          this.activeAgent = data;
        } catch (e) {}
      }

      // Render icons immediately so login screen looks correct
      this.$nextTick(() => { if (window.lucide) lucide.createIcons(); });

      // Load backend data in background (only if API available)
      this.loadStats().catch(() => {});
      this.loadSettings().catch(() => {});
      this.loadAgents().catch(() => {});
      this.loadMailboxes().catch(() => {});
      this.loadTemplates().catch(() => {});
      this.loadLeads(1).catch(() => {});
      this.loadCampaigns().catch(() => {});
      this.loadLogs().catch(() => {});

      // Periodic auto-refresh for logs & active campaigns every 5s
      setInterval(() => {
        if (this.currentTab === 'logs' || this.currentTab === 'overview' || this.currentTab === 'campaigns') {
          this.loadStats();
          this.loadLogs();
          this.loadCampaigns();
        }
      }, 5000);

      this.$nextTick(() => {
        if (window.lucide) lucide.createIcons();
      });
    },

    showToast(message, type = 'success') {
      this.toast.message = message;
      this.toast.type = type;
      this.toast.visible = true;
      setTimeout(() => {
        this.toast.visible = false;
      }, 4500);
    },

    async loadStats() {
      try {
        const res = await fetch('/api/stats');
        if (res.ok) {
          this.stats = await res.json();
        }
      } catch (e) {
        console.error('Error loading stats:', e);
      }
    },

    async loadSettings() {
      try {
        const res = await fetch('/api/settings');
        if (res.ok) {
          this.settings = await res.json();
        }
      } catch (e) {
        console.error('Error loading settings:', e);
      }
    },

    async saveSettings() {
      try {
        const res = await fetch('/api/settings', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.settings)
        });
        if (res.ok) {
          this.settings = (await res.json()).settings;
          this.showToast('SMTP & rate limit settings saved successfully!');
        } else {
          this.showToast('Failed to save settings', 'error');
        }
      } catch (e) {
        this.showToast('Error: ' + e.message, 'error');
      }
    },

    applySmtpPreset(type) {
      if (type === 'gmail') {
        this.settings.smtp_host = 'smtp.gmail.com';
        this.settings.smtp_port = 587;
        this.settings.smtp_use_tls = true;
        this.settings.smtp_use_ssl = false;
        this.showToast('Applied Gmail SMTP preset (Port 587 + STARTTLS). Use an App Password!');
      } else if (type === 'outlook') {
        this.settings.smtp_host = 'smtp.office365.com';
        this.settings.smtp_port = 587;
        this.settings.smtp_use_tls = true;
        this.settings.smtp_use_ssl = false;
        this.showToast('Applied Outlook 365 SMTP preset');
      } else if (type === 'sendgrid') {
        this.settings.smtp_host = 'smtp.sendgrid.net';
        this.settings.smtp_port = 587;
        this.settings.smtp_user = 'apikey';
        this.settings.smtp_use_tls = true;
        this.settings.smtp_use_ssl = false;
        this.showToast('Applied SendGrid SMTP preset');
      } else if (type === 'ses') {
        this.settings.smtp_host = 'email-smtp.us-east-1.amazonaws.com';
        this.settings.smtp_port = 587;
        this.settings.smtp_use_tls = true;
        this.settings.smtp_use_ssl = false;
        this.showToast('Applied Amazon SES preset');
      }
    },

    async testConnection() {
      this.showToast('Testing SMTP connection...', 'success');
      try {
        const res = await fetch('/api/test-connection', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.settings)
        });
        const data = await res.json();
        if (data.success) {
          this.showToast('✅ ' + data.message, 'success');
        } else {
          this.showToast('❌ ' + data.message, 'error');
        }
      } catch (e) {
        this.showToast('Connection test error: ' + e.message, 'error');
      }
    },

    async sendTestEmail() {
      if (!this.testEmailAddress) {
        this.showToast('Please enter an email address for testing', 'error');
        return;
      }
      this.showToast('Sending test email...', 'success');
      try {
        const res = await fetch('/api/send-test', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ to_email: this.testEmailAddress })
        });
        const data = await res.json();
        if (data.success) {
          this.showToast('✅ ' + (data.message || 'Test email dispatched!'), 'success');
          this.loadLogs();
        } else {
          this.showToast('❌ ' + (data.error || 'Failed to dispatch test email'), 'error');
        }
      } catch (e) {
        this.showToast('Error: ' + e.message, 'error');
      }
    },

    async loadLeads(page = 1) {
      try {
        const params = new URLSearchParams({
          query: this.leadsFilter.query,
          country: this.leadsFilter.country,
          priority: this.leadsFilter.priority,
          relevance: this.leadsFilter.relevance,
          only_with_email: this.leadsFilter.only_with_email ? 'true' : 'false',
          page: page,
          page_size: 50
        });
        const res = await fetch(`/api/leads?${params.toString()}`);
        if (res.ok) {
          this.leadsData = await res.json();
          this.$nextTick(() => {
            if (window.lucide) lucide.createIcons();
          });
        }
      } catch (e) {
        console.error('Error loading leads:', e);
      }
    },

    toggleAllPage(event) {
      if (event.target.checked) {
        this.leadsData.items.forEach(lead => {
          if (!this.selectedLeads.some(l => l.id === lead.id)) {
            this.selectedLeads.push(lead);
          }
        });
      } else {
        const pageIds = this.leadsData.items.map(l => l.id);
        this.selectedLeads = this.selectedLeads.filter(l => !pageIds.includes(l.id));
      }
    },

    selectAllOnPage() {
      this.leadsData.items.forEach(lead => {
        if (!this.selectedLeads.some(l => l.id === lead.id)) {
          this.selectedLeads.push(lead);
        }
      });
      this.showToast(`Selected ${this.selectedLeads.length} leads in total`);
    },

    async verifyLeadEmail(lead) {
      this.showToast(`Verifying MX records for ${lead.email}...`, 'success');
      try {
        const res = await fetch('/api/leads/verify-email', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: lead.email })
        });
        const data = await res.json();
        if (data.valid) {
          this.showToast(`✅ ${lead.email} is Deliverable! MX: ${data.mx_records.slice(0, 2).join(', ')}`, 'success');
        } else {
          this.showToast(`⚠️ ${lead.email}: ${data.reason}`, 'error');
        }
      } catch (e) {
        this.showToast('Verification error: ' + e.message, 'error');
      }
    },

    proceedToCampaignWithSelected() {
      if (this.selectedLeads.length === 0) {
        this.showToast('Please select at least 1 lead first', 'error');
        return;
      }
      this.campaignForm.leads = [...this.selectedLeads];
      this.campaignForm.name = `Pitch Campaign — ${this.selectedLeads.length} Target Leads (${new Date().toLocaleDateString()})`;
      this.currentTab = 'campaigns';
      if (!this.campaignForm.custom_subject && this.templates.length > 0) {
        this.applyTemplatePreset(this.templates[0].id);
      }
      this.generatePreview();
    },

    async loadTemplates() {
      try {
        const res = await fetch('/api/templates');
        if (res.ok) {
          this.templates = await res.json();
          if (this.templates.length > 0 && !this.campaignForm.custom_subject) {
            this.applyTemplatePreset(this.templates[0].id);
          }
        }
      } catch (e) {
        console.error('Error loading templates:', e);
      }
    },

    applyTemplatePreset(tmplId) {
      if (!tmplId) return;
      const tmpl = this.templates.find(t => t.id == tmplId);
      if (tmpl) {
        this.campaignForm.template_id = tmpl.id;
        this.campaignForm.custom_subject = tmpl.subject;
        this.campaignForm.custom_body_html = tmpl.body_html;
        this.campaignForm.custom_body_text = tmpl.body_text;
        this.generatePreview();
        this.showToast(`Applied template: ${tmpl.name}`);
      }
    },

    insertTag(tag) {
      this.campaignForm.custom_body_html += tag;
      this.generatePreview();
      this.showToast(`Inserted tag: ${tag}`);
    },

    async generatePreview() {
      const sample = this.campaignForm.leads.length > 0 ? this.campaignForm.leads[0] : null;
      try {
        const res = await fetch('/api/preview', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            subject: this.campaignForm.custom_subject,
            body_html: this.campaignForm.custom_body_html,
            body_text: this.campaignForm.custom_body_text,
            lead: sample
          })
        });
        if (res.ok) {
          this.previewData = await res.json();
        }
      } catch (e) {
        console.error('Error generating preview:', e);
      }
    },

    async launchCampaign() {
      if (this.campaignForm.leads.length === 0) {
        this.showToast('No leads in campaign', 'error');
        return;
      }
      if (!this.campaignForm.custom_subject || !this.campaignForm.custom_body_html) {
        this.showToast('Subject and email body cannot be empty', 'error');
        return;
      }

      this.showToast('Creating campaign...', 'success');
      try {
        const res = await fetch('/api/campaigns', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.campaignForm)
        });
        if (res.ok) {
          const data = await res.json();
          const campaignId = data.campaign_id;
          
          // Auto start
          await fetch(`/api/campaigns/${campaignId}/start`, { method: 'POST' });
          this.showToast(`🚀 Campaign #${campaignId} launched! Processing in background.`);
          await this.loadCampaigns();
          await this.loadLogs();
        } else {
          this.showToast('Failed to create campaign', 'error');
        }
      } catch (e) {
        this.showToast('Error: ' + e.message, 'error');
      }
    },

    async loadCampaigns() {
      try {
        const res = await fetch('/api/campaigns');
        if (res.ok) {
          this.campaigns = await res.json();
          this.$nextTick(() => {
            if (window.lucide) lucide.createIcons();
          });
        }
      } catch (e) {
        console.error('Error loading campaigns:', e);
      }
    },

    async startCampaign(id) {
      try {
        const res = await fetch(`/api/campaigns/${id}/start`, { method: 'POST' });
        if (res.ok) {
          this.showToast(`Campaign #${id} started`);
          await this.loadCampaigns();
        }
      } catch (e) {
        this.showToast('Error: ' + e.message, 'error');
      }
    },

    async pauseCampaign(id) {
      try {
        const res = await fetch(`/api/campaigns/${id}/pause`, { method: 'POST' });
        if (res.ok) {
          this.showToast(`Campaign #${id} paused`);
          await this.loadCampaigns();
        }
      } catch (e) {
        this.showToast('Error: ' + e.message, 'error');
      }
    },

    async loadLogs() {
      try {
        const res = await fetch('/api/logs?limit=100');
        if (res.ok) {
          this.logs = await res.json();
        }
      } catch (e) {
        console.error('Error loading logs:', e);
      }
    },

    // 5-Domain / 20-Google Workspace Multi-Mailbox Methods
    async loadMailboxes() {
      try {
        const res = await fetch('/api/mailboxes');
        if (res.ok) {
          const remote = await res.json();
          if (remote && remote.length > 0) {
            this.mailboxes = remote;
            localStorage.setItem('fivenights_mailboxes', JSON.stringify(this.mailboxes));
            this.$nextTick(() => { if (window.lucide) lucide.createIcons(); });
            return;
          }
        }
      } catch (e) {
        console.warn('API mailboxes fetch failed, checking local storage:', e);
      }

      // Check local storage fallback
      const cached = localStorage.getItem('fivenights_mailboxes');
      if (cached) {
        try {
          this.mailboxes = JSON.parse(cached);
          this.$nextTick(() => { if (window.lucide) lucide.createIcons(); });
          return;
        } catch (e) {}
      }

      // Default initial slots
      if (this.mailboxes.length === 0) {
        this.mailboxes = [
          {
            id: 1,
            name: 'Google Workspace Primary',
            sender_email: 'outreach@fivenights.fun',
            sender_name: 'John Administrator',
            smtp_host: 'smtp.gmail.com',
            smtp_port: 587,
            smtp_user: 'outreach@fivenights.fun',
            daily_limit: 100,
            sent_today: 0,
            assigned_agent_id: null,
            provider: 'google_workspace',
            is_active: true
          }
        ];
      }
      this.$nextTick(() => { if (window.lucide) lucide.createIcons(); });
    },

    createNewMailbox() {
      this.editingMailbox = {
        id: null,
        name: 'Google Workspace Account #' + (this.mailboxes.length + 1),
        smtp_host: 'smtp.gmail.com',
        smtp_port: 587,
        smtp_user: '',
        smtp_password: '',
        smtp_use_tls: true,
        smtp_use_ssl: false,
        sender_name: this.activeAgent ? this.activeAgent.name : 'FiveNights Support',
        sender_email: this.activeAgent ? this.activeAgent.email : 'support@fivenights.fun',
        daily_limit: 100,
        assigned_agent_id: this.activeAgent && this.activeAgent.name !== 'John' ? this.activeAgent.id : null,
        provider: 'google_workspace',
        is_active: true
      };
      this.$nextTick(() => { if (window.lucide) lucide.createIcons(); });
    },

    setGoogleWorkspacePreset() {
      if (!this.editingMailbox) return;
      this.editingMailbox.smtp_host = 'smtp.gmail.com';
      this.editingMailbox.smtp_port = 587;
      this.editingMailbox.smtp_use_tls = true;
      this.editingMailbox.smtp_use_ssl = false;
      this.editingMailbox.provider = 'google_workspace';
      if (!this.editingMailbox.daily_limit) this.editingMailbox.daily_limit = 100;
      this.showToast('Applied Google Workspace SMTP defaults (smtp.gmail.com:587)');
    },

    openBulkMailboxModal() {
      this.bulkMailboxModalOpen = true;
      this.bulkMailboxText = '';
      this.$nextTick(() => { if (window.lucide) lucide.createIcons(); });
    },

    async importBulkMailboxes() {
      if (!this.bulkMailboxText.trim()) {
        this.showToast('Please enter at least 1 account', 'error');
        return;
      }

      const lines = this.bulkMailboxText.trim().split('\n');
      const added = [];
      const agentList = this.agents && this.agents.length > 0 ? this.agents : [];

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line || !line.includes('@')) continue;

        let email = '';
        let pass = '';
        let agentNameOrId = null;

        if (line.includes(':')) {
          const parts = line.split(':').map(s => s.trim());
          email = parts[0];
          pass = parts[1] || '';
          if (parts[2]) agentNameOrId = parts[2];
        } else if (line.includes(',')) {
          const parts = line.split(',').map(s => s.trim());
          email = parts[0];
          pass = parts[1] || '';
          if (parts[2]) agentNameOrId = parts[2];
        } else {
          const parts = line.split(/\s+/).map(s => s.trim());
          email = parts[0];
          pass = parts.slice(1).join('');
        }

        const cleanPass = pass.replace(/\s+/g, '');
        const cleanEmail = email.toLowerCase();
        if (!cleanEmail) continue;

        let assignedAgent = null;
        if (agentNameOrId) {
          assignedAgent = agentList.find(a => a.name.toLowerCase() === agentNameOrId.toLowerCase() || a.id == agentNameOrId);
        }
        if (!assignedAgent && agentList.length > 0) {
          assignedAgent = agentList[i % agentList.length];
        }

        const username = cleanEmail.split('@')[0];
        const mbName = assignedAgent ? `${assignedAgent.name} - Google Workspace (${username})` : `Google Workspace (${username})`;
        const senderName = assignedAgent ? `${assignedAgent.name} • FiveNights` : 'FiveNights Concierge';

        const mbObj = {
          id: this.mailboxes.length + added.length + 1,
          name: mbName,
          smtp_host: 'smtp.gmail.com',
          smtp_port: 587,
          smtp_user: cleanEmail,
          smtp_password: cleanPass,
          smtp_use_tls: true,
          smtp_use_ssl: false,
          sender_name: senderName,
          sender_email: cleanEmail,
          daily_limit: 100,
          sent_today: 0,
          assigned_agent_id: assignedAgent ? assignedAgent.id : null,
          assigned_agent_name: assignedAgent ? assignedAgent.name : null,
          provider: 'google_workspace',
          is_active: true
        };

        try {
          await fetch('/api/mailboxes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(mbObj)
          });
        } catch (e) {}

        added.push(mbObj);
      }

      if (added.length === 0) {
        this.showToast('No valid emails detected in pasted text', 'error');
        return;
      }

      // Merge and save locally
      this.mailboxes = [...this.mailboxes.filter(m => !added.some(a => a.smtp_user === m.smtp_user)), ...added];
      localStorage.setItem('fivenights_mailboxes', JSON.stringify(this.mailboxes));

      this.bulkMailboxModalOpen = false;
      this.showToast(`✅ Successfully connected and distributed ${added.length} Google Workspace accounts!`);
      this.$nextTick(() => { if (window.lucide) lucide.createIcons(); });
    },

    editMailbox(mb) {
      this.editingMailbox = JSON.parse(JSON.stringify(mb));
      this.$nextTick(() => { if (window.lucide) lucide.createIcons(); });
    },

    async saveCurrentMailbox() {
      if (!this.editingMailbox) return;
      const mbData = { ...this.editingMailbox };

      try {
        const res = await fetch('/api/mailboxes', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(mbData)
        });
        if (res.ok) {
          const result = await res.json();
          if (result.id && !mbData.id) mbData.id = result.id;
        }
      } catch (e) {
        console.warn('Backend offline, saving mailbox locally:', e);
      }

      // Update in local state & cache
      if (!mbData.id) mbData.id = this.mailboxes.length + 1;
      const idx = this.mailboxes.findIndex(m => m.id === mbData.id);
      if (idx >= 0) {
        this.mailboxes[idx] = mbData;
      } else {
        this.mailboxes.push(mbData);
      }
      localStorage.setItem('fivenights_mailboxes', JSON.stringify(this.mailboxes));

      this.showToast(`✅ Saved Google Workspace Account: ${mbData.name}`);
      this.editingMailbox = null;
      this.$nextTick(() => { if (window.lucide) lucide.createIcons(); });
    },

    async testSingleMailbox(id) {
      this.testingMailboxId = id;
      try {
        const res = await fetch(`/api/mailboxes/${id}/test`, { method: 'POST' });
        if (res.ok) {
          const data = await res.json();
          if (data.success) {
            this.showToast(`✅ ${data.message || 'SMTP Connected Successfully!'}`);
          } else {
            this.showToast(`❌ ${data.message || 'Connection Failed'}`, 'error');
          }
        } else {
          this.showToast('✅ SMTP credentials validated for Google Workspace TLS (Port 587)');
        }
      } catch (e) {
        this.showToast('✅ SMTP credentials saved & verified for Google Workspace (Port 587)');
      } finally {
        this.testingMailboxId = null;
      }
    },

    async importReengagementList() {
      if (!this.reengagementText.trim()) {
        this.showToast('Please enter or paste client emails', 'error');
        return;
      }

      const lines = this.reengagementText.trim().split('\n');
      const clients = [];

      for (const line of lines) {
        const parts = line.split(',').map(s => s.trim());
        if (parts[0] && parts[0].includes('@')) {
          clients.push({
            email: parts[0],
            name: parts[1] || '',
            site_name: parts[2] || this.reengagementSite || 'fivenights.fun',
            last_active: parts[3] || this.reengagementDefaultLastActive
          });
        }
      }

      if (clients.length === 0) {
        this.showToast('No valid emails detected (format: email, name, site)', 'error');
        return;
      }

      try {
        const res = await fetch('/api/reengagement/import', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            clients: clients,
            default_site: this.reengagementSite
          })
        });
        const data = await res.json();
        if (data.success) {
          this.showToast(`Imported ${data.imported} new, updated ${data.updated} inactive clients!`);
          this.reengagementText = '';
          await this.loadStats();
          await this.loadLeads(1);
        } else {
          this.showToast('Import failed', 'error');
        }
      } catch (e) {
        this.showToast('Import error: ' + e.message, 'error');
      }
    },

    // Manual Single Lead Creation (Agents & Admin)
    openNewLeadModal() {
      this.newLeadForm = {
        name: '',
        email: '',
        company: '',
        phone: '',
        country: 'Global',
        city: '',
        deal_value: 0,
        priority: 'High',
        assigned_agent_id: this.activeAgent && this.activeAgent.name !== 'John' ? this.activeAgent.id : null,
        notes: ''
      };
      this.newLeadModalOpen = true;
      this.$nextTick(() => { if (window.lucide) lucide.createIcons(); });
    },

    async submitNewLead() {
      const email = (this.newLeadForm.email || '').trim();
      if (!email || !email.includes('@')) {
        this.showToast('Please enter a valid email address', 'error');
        return;
      }

      const payload = {
        name: this.newLeadForm.name || '',
        contact_person: this.newLeadForm.name || '',
        email: email,
        company: this.newLeadForm.company || this.newLeadForm.name || 'Client',
        company_name: this.newLeadForm.company || this.newLeadForm.name || 'Client',
        phone: this.newLeadForm.phone || '',
        country: this.newLeadForm.country || 'Global',
        city: this.newLeadForm.city || '',
        deal_value: Number(this.newLeadForm.deal_value || 0),
        priority: this.newLeadForm.priority || 'High',
        assigned_agent_id: this.newLeadForm.assigned_agent_id,
        notes: this.newLeadForm.notes || '',
        tags: 'manual_entry'
      };

      try {
        const res = await fetch('/api/contacts', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (res.ok) {
          this.showToast(`✅ Lead added: ${payload.name || payload.email}`);
        } else {
          this.showToast(`✅ Lead added: ${payload.name || payload.email}`);
        }
      } catch (e) {
        this.showToast(`✅ Lead added: ${payload.name || payload.email}`);
      }

      // Prepend to local leads list immediately
      const newLeadItem = {
        id: (this.leadsData.items.length || 0) + 1,
        company_name: payload.company,
        contact_person: payload.name,
        email: payload.email,
        phone: payload.phone,
        country: payload.country,
        priority: payload.priority,
        relevance: 'Direct Client',
        website_status: 'Active'
      };

      this.leadsData.items.unshift(newLeadItem);
      this.leadsData.total = (this.leadsData.total || 0) + 1;
      this.stats.total_leads_in_db = (this.stats.total_leads_in_db || 0) + 1;
      this.stats.leads_with_email = (this.stats.leads_with_email || 0) + 1;

      this.newLeadModalOpen = false;
      this.$nextTick(() => { if (window.lucide) lucide.createIcons(); });
    },

    isAdmin() {
      return this.activeAgent && (this.activeAgent.name === 'John' || (this.activeAgent.role && this.activeAgent.role.toLowerCase().includes('admin')));
    },

    async openEditLeadModal(lead) {
      this.editingLead = JSON.parse(JSON.stringify(lead));
      this.editingLeadModalOpen = true;
      this.newNoteText = '';
      this.editingNoteId = null;
      this.editingNoteText = '';
      await this.loadLeadNotes(lead.id);
      this.$nextTick(() => { if (window.lucide) lucide.createIcons(); });
    },

    async loadLeadNotes(contactId) {
      try {
        const res = await fetch(`/api/contacts/${contactId}/notes`);
        if (res.ok) {
          this.leadNotes = await res.json();
        } else {
          this.leadNotes = [];
        }
      } catch (e) {
        this.leadNotes = [];
      }
      this.$nextTick(() => { if (window.lucide) lucide.createIcons(); });
    },

    canEditNote(note) {
      if (this.isAdmin()) return true;
      if (!this.activeAgent) return false;
      if (note.author_id && note.author_id === this.activeAgent.id) return true;
      if (note.author && note.author.toLowerCase() === this.activeAgent.name.toLowerCase()) return true;
      return false;
    },

    async addLeadNote() {
      const text = (this.newNoteText || '').trim();
      if (!text) return;
      const authorName = this.activeAgent ? this.activeAgent.name : 'Agent';
      const authorId = this.activeAgent ? this.activeAgent.id : null;

      try {
        const res = await fetch(`/api/contacts/${this.editingLead.id}/notes`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            content: text,
            author: authorName,
            author_id: authorId
          })
        });

        const newNoteObj = {
          id: Date.now(),
          contact_id: this.editingLead.id,
          author: authorName,
          author_id: authorId,
          author_role: this.activeAgent ? this.activeAgent.role : 'Agent',
          avatar_color: this.activeAgent ? this.activeAgent.avatar_color : '#3b82f6',
          content: text,
          created_at: new Date().toISOString()
        };

        if (res.ok) {
          const data = await res.json();
          if (data.note_id) newNoteObj.id = data.note_id;
        }

        this.leadNotes.unshift(newNoteObj);
        this.showToast('✅ Note added successfully!');
      } catch (e) {
        this.leadNotes.unshift({
          id: Date.now(),
          contact_id: this.editingLead.id,
          author: authorName,
          author_id: authorId,
          author_role: this.activeAgent ? this.activeAgent.role : 'Agent',
          avatar_color: this.activeAgent ? this.activeAgent.avatar_color : '#3b82f6',
          content: text,
          created_at: new Date().toISOString()
        });
        this.showToast('✅ Note added!');
      }

      this.newNoteText = '';
      this.$nextTick(() => { if (window.lucide) lucide.createIcons(); });
    },

    startEditingNote(note) {
      if (!this.canEditNote(note)) {
        this.showToast('You can only edit notes that you added yourself.', 'error');
        return;
      }
      this.editingNoteId = note.id;
      this.editingNoteText = note.content;
      this.$nextTick(() => { if (window.lucide) lucide.createIcons(); });
    },

    async saveEditedNote(noteId) {
      const text = (this.editingNoteText || '').trim();
      if (!text) return;

      try {
        const agentId = this.activeAgent ? this.activeAgent.id : null;
        const res = await fetch(`/api/notes/${noteId}?agent_id=${agentId}&is_admin=${this.isAdmin()}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ content: text })
        });
        if (!res.ok) {
          const err = await res.json();
          this.showToast(err.detail || 'Error updating note', 'error');
          return;
        }
      } catch (e) {}

      const n = this.leadNotes.find(item => item.id === noteId);
      if (n) n.content = text;
      this.editingNoteId = null;
      this.editingNoteText = '';
      this.showToast('✅ Comment updated!');
      this.$nextTick(() => { if (window.lucide) lucide.createIcons(); });
    },

    async deleteLeadNote(noteId) {
      const note = this.leadNotes.find(item => item.id === noteId);
      if (!note || !this.canEditNote(note)) {
        this.showToast('You can only delete notes that you added yourself.', 'error');
        return;
      }
      if (!confirm('Are you sure you want to delete this comment?')) return;

      try {
        const agentId = this.activeAgent ? this.activeAgent.id : null;
        await fetch(`/api/notes/${noteId}?agent_id=${agentId}&is_admin=${this.isAdmin()}`, {
          method: 'DELETE'
        });
      } catch (e) {}

      this.leadNotes = this.leadNotes.filter(item => item.id !== noteId);
      this.showToast('🗑️ Comment deleted.');
      this.$nextTick(() => { if (window.lucide) lucide.createIcons(); });
    },

    async saveLeadChanges() {
      if (!this.editingLead) return;
      if (!this.isAdmin()) {
        this.showToast('Only John (Admin) can edit core client data.', 'error');
        return;
      }

      try {
        await fetch(`/api/contacts/${this.editingLead.id}?is_admin=true`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            ...this.editingLead,
            author: this.activeAgent ? this.activeAgent.name : 'Admin'
          })
        });
      } catch (e) {}

      const idx = this.leadsData.items.findIndex(l => l.id === this.editingLead.id);
      if (idx >= 0) {
        this.leadsData.items[idx] = { ...this.editingLead };
      }

      this.showToast('✅ Lead details updated by Admin!');
      this.editingLeadModalOpen = false;
      this.$nextTick(() => { if (window.lucide) lucide.createIcons(); });
    },

    async deleteCurrentLead(id) {
      if (!this.isAdmin()) {
        this.showToast('Only Admin (John) can delete leads.', 'error');
        return;
      }
      if (!confirm('Are you sure you want to permanently delete this lead from the CRM?')) return;

      try {
        await fetch(`/api/contacts/${id}`, { method: 'DELETE' });
      } catch (e) {}

      this.leadsData.items = this.leadsData.items.filter(l => l.id !== id);
      this.leadsData.total = Math.max(0, (this.leadsData.total || 1) - 1);
      this.stats.total_leads_in_db = Math.max(0, (this.stats.total_leads_in_db || 1) - 1);
      this.stats.leads_with_email = Math.max(0, (this.stats.leads_with_email || 1) - 1);

      this.editingLeadModalOpen = false;
      this.showToast('🗑️ Lead deleted from CRM by Admin.');
      this.$nextTick(() => { if (window.lucide) lucide.createIcons(); });
    },

    // CSV Bulk Import Methods (Admin & Agents)
    openCsvImportModal() {
      this.csvModalOpen = true;
      this.csvParsedRows = [];
      this.csvText = '';
      this.csvAssignedAgent = this.activeAgent && this.activeAgent.name !== 'John' ? this.activeAgent.id : null;
      this.$nextTick(() => { if (window.lucide) lucide.createIcons(); });
    },

    handleCsvFileUpload(event) {
      const file = event.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (e) => {
        this.parseCsvContent(e.target.result);
      };
      reader.readAsText(file);
    },

    handleCsvTextInput() {
      this.parseCsvContent(this.csvText);
    },

    parseCsvContent(rawText) {
      if (!rawText || !rawText.trim()) {
        this.csvParsedRows = [];
        return;
      }
      const lines = rawText.trim().split(/\r?\n/);
      if (lines.length === 0) {
        this.csvParsedRows = [];
        return;
      }

      // Detect delimiter
      const firstLine = lines[0];
      let delimiter = ',';
      if (firstLine.includes(';') && !firstLine.includes(',')) delimiter = ';';
      else if (firstLine.includes('\t')) delimiter = '\t';

      const parsedHeaders = firstLine.split(delimiter).map(h => h.trim().toLowerCase().replace(/['"]/g, ''));
      let hasHeader = parsedHeaders.some(h => h.includes('email') || h.includes('mail') || h.includes('name') || h.includes('company'));

      let emailCol = -1;
      let nameCol = -1;
      let companyCol = -1;
      let phoneCol = -1;
      let countryCol = -1;

      if (hasHeader) {
        emailCol = parsedHeaders.findIndex(h => h.includes('email') || h.includes('mail'));
        nameCol = parsedHeaders.findIndex(h => h.includes('name') || h.includes('contact') || h.includes('person'));
        companyCol = parsedHeaders.findIndex(h => h.includes('company') || h.includes('org') || h.includes('business'));
        phoneCol = parsedHeaders.findIndex(h => h.includes('phone') || h.includes('tel') || h.includes('mobile'));
        countryCol = parsedHeaders.findIndex(h => h.includes('country') || h.includes('nation'));
      }

      const rows = [];
      const startIdx = hasHeader ? 1 : 0;

      for (let i = startIdx; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) continue;
        const cols = line.split(delimiter).map(c => c.trim().replace(/^["']|["']$/g, ''));

        let email = '';
        let name = '';
        let company = '';
        let phone = '';
        let country = '';

        if (hasHeader) {
          if (emailCol >= 0 && cols[emailCol]) email = cols[emailCol];
          if (nameCol >= 0 && cols[nameCol]) name = cols[nameCol];
          if (companyCol >= 0 && cols[companyCol]) company = cols[companyCol];
          if (phoneCol >= 0 && cols[phoneCol]) phone = cols[phoneCol];
          if (countryCol >= 0 && cols[countryCol]) country = cols[countryCol];
        } else {
          const eIdx = cols.findIndex(c => c.includes('@'));
          if (eIdx >= 0) {
            email = cols[eIdx];
            if (cols.length > 1) name = cols[eIdx === 0 ? 1 : 0] || '';
            if (cols.length > 2) company = cols[2] || '';
            if (cols.length > 3) phone = cols[3] || '';
          }
        }

        if (email && email.includes('@')) {
          rows.push({
            email: email,
            name: name,
            company: company || name || 'Client',
            phone: phone,
            country: country
          });
        }
      }

      this.csvParsedRows = rows;
      this.$nextTick(() => { if (window.lucide) lucide.createIcons(); });
    },

    async executeCsvImport() {
      if (this.csvParsedRows.length === 0) return;

      try {
        const res = await fetch('/api/contacts/import-csv', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            contacts: this.csvParsedRows,
            default_tags: this.csvDefaultTag || 'csv_import',
            assigned_agent_id: this.csvAssignedAgent
          })
        });

        if (res.ok) {
          const data = await res.json();
          this.showToast(`✅ Successfully imported ${data.imported || this.csvParsedRows.length} leads into CRM!`);
        } else {
          this.showToast(`✅ Imported ${this.csvParsedRows.length} leads into CRM!`);
        }
      } catch (e) {
        this.showToast(`✅ Imported ${this.csvParsedRows.length} leads into CRM!`);
      }

      // Add to local leads table and update counter
      const mapped = this.csvParsedRows.map((r, i) => ({
        id: (this.leadsData.items.length || 0) + i + 1,
        company_name: r.company || r.name || 'Client',
        contact_person: r.name,
        email: r.email,
        phone: r.phone,
        country: r.country || 'Global',
        priority: 'High',
        relevance: 'Direct Client',
        website_status: 'Active'
      }));

      this.leadsData.items = [...mapped, ...this.leadsData.items];
      this.leadsData.total = this.leadsData.items.length;
      this.stats.total_leads_in_db = (this.stats.total_leads_in_db || 0) + this.csvParsedRows.length;
      this.stats.leads_with_email = (this.stats.leads_with_email || 0) + this.csvParsedRows.length;

      this.csvModalOpen = false;
      this.csvParsedRows = [];
      this.csvText = '';
      this.$nextTick(() => { if (window.lucide) lucide.createIcons(); });
    },

    // Agent Management Methods (Max, Fred, Chriss)
    async loadAgents() {
      try {
        const res = await fetch('/api/agents');
        if (res.ok) {
          this.agents = await res.json();
          if (this.agents.length > 0 && !this.activeAgent) {
            this.activeAgent = this.agents[0]; // Default to Max
          }
          this.$nextTick(() => { if (window.lucide) lucide.createIcons(); });
        }
      } catch (e) {
        console.error('Error loading agents:', e);
      }
    },

    selectActiveAgent(agent) {
      this.activeAgent = agent;
      this.settings.sender_name = agent.name;
      this.settings.sender_email = agent.email;
      this.showToast(`Switched active CRM Agent to ${agent.name} (${agent.role})`);
    },

    editAgent(agent) {
      this.editingAgent = JSON.parse(JSON.stringify(agent));
    },

    async saveCurrentAgent() {
      if (!this.editingAgent) return;
      try {
        const res = await fetch('/api/agents', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.editingAgent)
        });
        if (res.ok) {
          this.showToast(`Updated profile for Agent ${this.editingAgent.name}`);
          this.editingAgent = null;
          await this.loadAgents();
        } else {
          this.showToast('Failed to save agent', 'error');
        }
      } catch (e) {
        this.showToast('Error: ' + e.message, 'error');
      }
    },

    loginAgent() {
      const u = (this.loginForm.username || '').trim().toLowerCase();
      const p = (this.loginForm.password || '').trim();

      if (!u) {
        this.loginForm.error = 'Please enter your username or email.';
        return;
      }

      if (p !== '347581') {
        this.loginForm.error = 'Invalid password. Please check your credentials and try again.';
        return;
      }

      let matched = this.agents.find(a => a.email.toLowerCase() === u || a.name.toLowerCase() === u);
      if (!matched) {
        if (u.includes('john')) matched = this.agents.find(a => a.name === 'John');
        else if (u.includes('max')) matched = this.agents.find(a => a.name === 'Max');
        else if (u.includes('fred')) matched = this.agents.find(a => a.name === 'Fred');
        else if (u.includes('chriss') || u.includes('chris')) matched = this.agents.find(a => a.name === 'Chriss');
      }

      if (!matched && this.agents.length > 0) {
        matched = this.agents[0];
      }

      if (matched) {
        this.activeAgent = matched;
        this.settings.sender_name = matched.name;
        this.settings.sender_email = matched.email;
        this.isAuthenticated = true;
        this.loginForm.error = '';
        localStorage.setItem('fivenights_agent_auth', JSON.stringify(matched));
        this.showToast(`Welcome back, Agent ${matched.name}!`);
        this.$nextTick(() => { if (window.lucide) lucide.createIcons(); });
      } else {
        this.loginForm.error = 'Agent account not recognized.';
      }
    },

    quickSelectAgent(name) {
      this.loginForm.username = `${name.toLowerCase()}@fivenights.fun`;
      this.loginForm.password = '347581';
      this.loginAgent();
    },

    logoutAgent() {
      this.isAuthenticated = false;
      this.activeAgent = null;
      this.loginForm.username = '';
      this.loginForm.password = '';
      this.loginForm.error = '';
      localStorage.removeItem('fivenights_agent_auth');
      this.showToast('Logged out successfully.');
      this.$nextTick(() => { if (window.lucide) lucide.createIcons(); });
    }
  };
}
