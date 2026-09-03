function app() {
  return {
    currentTab: 'overview',
    stats: {},
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
      // Check saved authentication
      const savedAuth = localStorage.getItem('fivenights_agent_auth');
      if (savedAuth) {
        try {
          const data = JSON.parse(savedAuth);
          this.isAuthenticated = true;
          this.activeAgent = data;
        } catch (e) {}
      }

      await this.loadStats();
      await this.loadSettings();
      await this.loadAgents();
      await this.loadMailboxes();
      await this.loadTemplates();
      await this.loadLeads(1);
      await this.loadCampaigns();
      await this.loadLogs();

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

    // 5-Domain Multi-Mailbox Methods
    async loadMailboxes() {
      try {
        const res = await fetch('/api/mailboxes');
        if (res.ok) {
          this.mailboxes = await res.json();
          this.$nextTick(() => { if (window.lucide) lucide.createIcons(); });
        }
      } catch (e) {
        console.error('Error loading mailboxes:', e);
      }
    },

    editMailbox(mb) {
      this.editingMailbox = JSON.parse(JSON.stringify(mb));
    },

    async saveCurrentMailbox() {
      if (!this.editingMailbox) return;
      try {
        const res = await fetch('/api/mailboxes', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.editingMailbox)
        });
        if (res.ok) {
          this.showToast(`Saved configuration for ${this.editingMailbox.name}`);
          this.editingMailbox = null;
          await this.loadMailboxes();
        } else {
          this.showToast('Failed to save mailbox', 'error');
        }
      } catch (e) {
        this.showToast('Error: ' + e.message, 'error');
      }
    },

    async testSingleMailbox(id) {
      this.testingMailboxId = id;
      try {
        const res = await fetch(`/api/mailboxes/${id}/test`, { method: 'POST' });
        const data = await res.json();
        if (data.success) {
          this.showToast(`✅ ${data.message || 'SMTP Connected Successfully!'}`);
        } else {
          this.showToast(`❌ ${data.message || 'Connection Failed'}`, 'error');
        }
      } catch (e) {
        this.showToast('Test failed: ' + e.message, 'error');
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
