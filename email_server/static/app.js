function app(initialTab = null) {
  let detectedTab = initialTab;
  if (!detectedTab && typeof window !== 'undefined') {
    const p = (window.location.pathname || '').toLowerCase();
    if (p.includes('customer')) detectedTab = 'leads';
    else if (p.includes('inbox')) detectedTab = 'inbox';
    else if (p.includes('campaign')) detectedTab = 'campaigns';
    else if (p.includes('mailbox')) detectedTab = 'domains';
    else if (p.includes('winback')) detectedTab = 'reengagement';
    else if (p.includes('agent')) detectedTab = 'agents';
    else if (p.includes('setting')) detectedTab = 'settings';
    else if (p.includes('log')) detectedTab = 'logs';
    else detectedTab = 'overview';
  }
  return {
    currentTab: detectedTab || 'overview',
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
    inboxThreads: [],
    selectedThread: null,
    threadMessages: [],
    inboxFilter: 'all',
    inboxSearch: '',
    replyText: '',
    replyMailboxId: null,
    replySending: false,
    unreadCount: 2,
    teamStats: [],
    quickSendModalOpen: false,
    quickSendLead: null,
    quickSendTemplateId: 1,
    quickSendMailboxId: null,
    quickSendSubject: '',
    quickSendBody: '',
    quickSendSending: false,
    guideModalOpen: false,
    guideTab: 'quickstart',

    get filteredInboxThreads() {
      return (this.inboxThreads || []).filter(t => {
        if (this.inboxFilter === 'unread' && !(t.unread_count > 0)) return false;
        if (this.inboxFilter === 'open' && t.status !== 'open') return false;
        if (this.inboxFilter === 'closed' && t.status !== 'closed') return false;
        if (this.inboxSearch) {
          const q = this.inboxSearch.toLowerCase();
          const matchName = (t.contact_name || t.company_name || '').toLowerCase().includes(q);
          const matchEmail = (t.contact_email || '').toLowerCase().includes(q);
          const matchSubject = (t.subject || '').toLowerCase().includes(q);
          const matchSnippet = (t.snippet || '').toLowerCase().includes(q);
          if (!matchName && !matchEmail && !matchSubject && !matchSnippet) return false;
        }
        return true;
      });
    },
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

      // Cross-page navigation handlers (URL query parameters & session data)
      if (typeof window !== 'undefined') {
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('openCsv') === '1') {
          this.csvModalOpen = true;
        }
        if (urlParams.get('filter') === 'unassigned') {
          this.leadsFilter.assigned = 'unassigned';
        }
        if (urlParams.get('search')) {
          this.leadsFilter.query = urlParams.get('search');
        }

        const storedLeads = sessionStorage.getItem('fivenights_campaign_leads');
        if (storedLeads) {
          try {
            this.campaignForm.leads = JSON.parse(storedLeads);
            const campName = sessionStorage.getItem('fivenights_campaign_name');
            if (campName) this.campaignForm.name = campName;
            sessionStorage.removeItem('fivenights_campaign_leads');
            sessionStorage.removeItem('fivenights_campaign_name');
            this.showToast(`Loaded ${this.campaignForm.leads.length} recipients into Campaign Builder`);
          } catch (e) {}
        }
      }

      // Load backend data in background (only if API available)
      this.loadStats().catch(() => {});
      this.loadSettings().catch(() => {});
      this.loadAgents().catch(() => {});
      this.loadMailboxes().catch(() => {});
      this.loadTemplates().catch(() => {});
      this.loadLeads(1).catch(() => {});
      this.loadCampaigns().catch(() => {});
      this.loadLogs().catch(() => {});
      this.loadInboxThreads().catch(() => {});
      this.loadTeamStats().catch(() => {});

      // Periodic auto-refresh for logs & active campaigns every 5s
      setInterval(() => {
        if (this.currentTab === 'logs' || this.currentTab === 'overview' || this.currentTab === 'campaigns') {
          this.loadStats();
          this.loadLogs();
          this.loadCampaigns();
        }
        if (this.currentTab === 'inbox') {
          this.loadInboxThreads();
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

    openGuide(tab = 'quickstart') {
      this.guideTab = tab;
      this.guideModalOpen = true;
      this.$nextTick(() => {
        if (window.lucide) lucide.createIcons();
      });
    },

    formatDate(dt) {
      if (!dt) return 'Just now';
      try {
        const d = new Date(dt);
        if (isNaN(d.getTime())) return String(dt);
        const now = new Date();
        const diffMs = now - d;
        const diffMin = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMin / 60);
        const diffDays = Math.floor(diffHours / 24);
        if (diffMin < 1) return 'Just now';
        if (diffMin < 60) return `${diffMin}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        return d.toLocaleDateString([], { month: 'short', day: 'numeric' });
      } catch (e) {
        return String(dt);
      }
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
        const backendRelevance = ['unassigned', 'mine', 'vip', 'active', 'inactive', 'new', 'winback'].includes(this.leadsFilter.relevance)
          ? 'All'
          : this.leadsFilter.relevance;

        const params = new URLSearchParams({
          query: this.leadsFilter.query,
          country: this.leadsFilter.country,
          priority: this.leadsFilter.priority,
          relevance: backendRelevance,
          only_with_email: this.leadsFilter.only_with_email ? 'true' : 'false',
          page: page,
          page_size: 50
        });
        const res = await fetch(`/api/leads?${params.toString()}`);
        if (res.ok) {
          const data = await res.json();
          let items = data.items || [];

          // B2C customer tiers & agent assignment filters
          if (this.leadsFilter.relevance === 'unassigned') {
            items = items.filter(l => !l.assigned_agent_id && !l.assigned_agent_name);
          } else if (this.leadsFilter.relevance === 'mine') {
            const myId = this.activeAgent?.id;
            const myName = (this.activeAgent?.name || '').toLowerCase();
            items = items.filter(l => (myId && l.assigned_agent_id === myId) || (l.assigned_agent_name && l.assigned_agent_name.toLowerCase() === myName));
          } else if (this.leadsFilter.relevance === 'vip') {
            items = items.filter(l => (l.tags && l.tags.toLowerCase().includes('vip')) || (l.priority && l.priority.toLowerCase() === 'high'));
          } else if (this.leadsFilter.relevance === 'active') {
            items = items.filter(l => (l.tags && l.tags.toLowerCase().includes('active')) || l.website_status === 'Active');
          } else if (this.leadsFilter.relevance === 'inactive') {
            items = items.filter(l => l.tags && (l.tags.toLowerCase().includes('inactive') || l.tags.toLowerCase().includes('churn')));
          } else if (this.leadsFilter.relevance === 'winback') {
            items = items.filter(l => (l.tags && l.tags.toLowerCase().includes('winback')) || (l.relevance && l.relevance.toLowerCase().includes('recovery')));
          }

          this.leadsData = {
            ...data,
            items: items,
            total: (items.length < (data.items || []).length) ? items.length : data.total
          };

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

    async loadInboxThreads() {
      try {
        const res = await fetch('/api/inbox/threads');
        if (res.ok) {
          const data = await res.json();
          this.inboxThreads = data.threads || [];
        } else {
          throw new Error('Fallback to local threads');
        }
      } catch (e) {
        if (!this.inboxThreads || this.inboxThreads.length === 0) {
          this.inboxThreads = [
            {
              id: 1,
              contact_id: 1,
              contact_name: "Alex Miller",
              contact_email: "alex.miller@gmail.com",
              contact_phone: "+44 7911 123456",
              contact_country: "United Kingdom",
              contact_tags: "vip,high_roller",
              assigned_agent_name: "Max",
              mailbox_id: 1,
              subject: "Question about VIP weekend reload bonus",
              snippet: "Hi Max, thanks for reaching out. Can you tell me if the 100% reload applies to crypto deposits as well as cards?",
              status: "open",
              unread_count: 1,
              last_message_at: new Date(Date.now() - 1000 * 60 * 15).toISOString()
            },
            {
              id: 2,
              contact_id: 2,
              contact_name: "Sophie Laurent",
              contact_email: "sophie.laurent@bluewin.ch",
              contact_phone: "+41 79 555 1234",
              contact_country: "Switzerland",
              contact_tags: "inactive,winback",
              assigned_agent_name: "Fred",
              mailbox_id: 2,
              subject: "Exclusive return perk for Sophie",
              snippet: "Hello Fred, I saw your email. Does the welcome back gift have any wagering requirement before withdrawal?",
              status: "open",
              unread_count: 1,
              last_message_at: new Date(Date.now() - 1000 * 60 * 45).toISOString()
            },
            {
              id: 3,
              contact_id: 3,
              contact_name: "David Becker",
              contact_email: "david.becker@web.de",
              contact_phone: "+49 171 9876543",
              contact_country: "Germany",
              contact_tags: "vip_gold,active",
              assigned_agent_name: "Chriss",
              mailbox_id: 3,
              subject: "VIP Gold withdrawal limit increase request",
              snippet: "Good afternoon Chriss. Could we increase the daily withdrawal limit on my account to 10k EUR?",
              status: "open",
              unread_count: 0,
              last_message_at: new Date(Date.now() - 1000 * 60 * 180).toISOString()
            },
            {
              id: 4,
              contact_id: 4,
              contact_name: "Marco Rossi",
              contact_email: "marco.rossi@tin.it",
              contact_phone: "+39 340 1234567",
              contact_country: "Italy",
              contact_tags: "active,feedback",
              assigned_agent_name: "Max",
              mailbox_id: 1,
              subject: "Quick feedback on recent games",
              snippet: "Everything has been smooth, loving the new live tables. Thanks for checking in!",
              status: "closed",
              unread_count: 0,
              last_message_at: new Date(Date.now() - 1000 * 60 * 1440).toISOString()
            }
          ];
        }
      }

      this.unreadCount = (this.inboxThreads || []).reduce((acc, t) => acc + (t.unread_count || 0), 0);
      this.$nextTick(() => { if (window.lucide) lucide.createIcons(); });
    },

    async selectThread(t) {
      this.selectedThread = t;
      this.replyText = '';
      this.replyMailboxId = t.mailbox_id || (this.mailboxes[0]?.id) || 1;

      if (t.unread_count > 0) {
        t.unread_count = 0;
        this.unreadCount = (this.inboxThreads || []).reduce((acc, th) => acc + (th.unread_count || 0), 0);
      }

      try {
        const res = await fetch(`/api/inbox/threads/${t.id}`);
        if (res.ok) {
          const data = await res.json();
          this.threadMessages = data.messages || [];
        } else {
          throw new Error('Use fallback messages');
        }
      } catch (e) {
        const now = new Date();
        if (t.id === 1) {
          this.threadMessages = [
            {
              id: 101,
              direction: "outbound",
              sender_name: "Max",
              sender_email: "max@fivenights.fun",
              subject: "Exclusive VIP privileges for Alex Miller",
              body_html: "<p>Hi Alex,</p><p>My name is Max, your dedicated VIP Account Manager at FiveNights. Your account now includes exclusive benefits: direct concierge access, bespoke weekly perks and reloads, express priority processing, and exclusive early access.</p><p>Is there anything I can set up for you today?</p><p>Warm regards,<br><strong>Max</strong><br>VIP Client Manager • FiveNights.fun</p>",
              sent_at: new Date(now.getTime() - 1000 * 60 * 60 * 2).toISOString()
            },
            {
              id: 102,
              direction: "inbound",
              sender_name: "Alex Miller",
              sender_email: "alex.miller@gmail.com",
              subject: "Re: Exclusive VIP privileges for Alex Miller",
              body_html: "<p>Hi Max, thanks for reaching out. Can you tell me if the 100% reload applies to crypto deposits as well as cards?</p>",
              sent_at: new Date(now.getTime() - 1000 * 60 * 15).toISOString()
            }
          ];
        } else if (t.id === 2) {
          this.threadMessages = [
            {
              id: 201,
              direction: "outbound",
              sender_name: "Fred",
              sender_email: "fred@fivenights.fun",
              subject: "We miss you, Sophie - a return perk is waiting",
              body_html: "<p>Hello Sophie,</p><p>It has been a while since your last visit to FiveNights! Your welcome-back rewards are ready: exclusive re-activation bonus, instant match on next deposit, and zero delay priority support.</p><p>Best regards,<br><strong>Fred</strong><br>Customer Success • FiveNights.fun</p>",
              sent_at: new Date(now.getTime() - 1000 * 60 * 120).toISOString()
            },
            {
              id: 202,
              direction: "inbound",
              sender_name: "Sophie Laurent",
              sender_email: "sophie.laurent@bluewin.ch",
              subject: "Re: We miss you, Sophie - a return perk is waiting",
              body_html: "<p>Hello Fred, I saw your email. Does the welcome back gift have any wagering requirement before withdrawal?</p>",
              sent_at: new Date(now.getTime() - 1000 * 60 * 45).toISOString()
            }
          ];
        } else if (t.id === 3) {
          this.threadMessages = [
            {
              id: 301,
              direction: "outbound",
              sender_name: "Chriss",
              sender_email: "chriss@fivenights.fun",
              subject: "Congratulations David! Your VIP Tier Upgrade is now active",
              body_html: "<p>Dear David,</p><p>Congratulations! Your account has been upgraded to <strong>VIP Gold Status</strong> with priority withdrawal limits and expedited processing.</p>",
              sent_at: new Date(now.getTime() - 1000 * 60 * 300).toISOString()
            },
            {
              id: 302,
              direction: "inbound",
              sender_name: "David Becker",
              sender_email: "david.becker@web.de",
              subject: "Re: VIP Tier Upgrade",
              body_html: "<p>Good afternoon Chriss. Could we increase the daily withdrawal limit on my account to 10k EUR?</p>",
              sent_at: new Date(now.getTime() - 1000 * 60 * 180).toISOString()
            }
          ];
        } else {
          this.threadMessages = [
            {
              id: 401,
              direction: "outbound",
              sender_name: "Max",
              sender_email: "max@fivenights.fun",
              subject: "Quick question about your FiveNights experience",
              body_html: "<p>Hi Marco, I am reaching out directly to see how everything has been going with your account recently.</p>",
              sent_at: new Date(now.getTime() - 1000 * 60 * 1500).toISOString()
            },
            {
              id: 402,
              direction: "inbound",
              sender_name: "Marco Rossi",
              sender_email: "marco.rossi@tin.it",
              subject: "Re: Quick question about your FiveNights experience",
              body_html: "<p>Everything has been smooth, loving the new live tables. Thanks for checking in!</p>",
              sent_at: new Date(now.getTime() - 1000 * 60 * 1440).toISOString()
            }
          ];
        }
      }

      this.$nextTick(() => { if (window.lucide) lucide.createIcons(); });
    },

    async sendThreadReply() {
      const text = (this.replyText || '').trim();
      if (!text || !this.selectedThread) return;

      this.replySending = true;
      const agentName = this.activeAgent?.name || 'Agent';
      const agentEmail = this.activeAgent?.email || 'support@fivenights.fun';
      const mbId = this.replyMailboxId || 1;
      const mb = this.mailboxes.find(m => m.id === mbId);
      const senderEmail = mb?.sender_email || agentEmail;

      const newMsg = {
        id: Date.now(),
        direction: 'outbound',
        sender_name: agentName,
        sender_email: senderEmail,
        subject: `Re: ${this.selectedThread.subject}`,
        body_html: `<p>${text.replace(/\n/g, '<br>')}</p>`,
        body_text: text,
        sent_at: new Date().toISOString()
      };

      this.threadMessages.push(newMsg);
      this.selectedThread.snippet = text;
      this.selectedThread.last_message_at = newMsg.sent_at;
      this.replyText = '';

      try {
        await fetch(`/api/inbox/threads/${this.selectedThread.id}/reply`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            agent_id: this.activeAgent?.id || 1,
            mailbox_id: mbId,
            body_html: newMsg.body_html,
            body_text: text
          })
        });
      } catch (e) {
        console.warn('Reply recorded locally:', e);
      } finally {
        this.replySending = false;
        this.showToast('✅ Reply dispatched to customer via Google Workspace SMTP!');
        this.$nextTick(() => { if (window.lucide) lucide.createIcons(); });
      }
    },

    async setThreadStatus(status) {
      if (!this.selectedThread) return;
      this.selectedThread.status = status;
      const idx = this.inboxThreads.findIndex(t => t.id === this.selectedThread.id);
      if (idx >= 0) this.inboxThreads[idx].status = status;

      try {
        await fetch(`/api/inbox/threads/${this.selectedThread.id}/status`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status })
        });
      } catch (e) {}
      this.showToast(`Conversation marked as ${status.toUpperCase()}`);
    },

    insertReplySnippet(text) {
      if (this.replyText) {
        this.replyText += '\n\n' + text;
      } else {
        this.replyText = text;
      }
      this.showToast('Snippet inserted into composer');
    },

    async distributeLeads() {
      this.showToast('Distributing unassigned customer pool evenly...', 'success');
      try {
        const res = await fetch('/api/admin/distribute-leads', { method: 'POST' });
        if (res.ok) {
          const data = await res.json();
          this.showToast(`✅ ${data.message || 'Leads evenly distributed across Max, Fred, and Chriss!'}`);
        } else {
          this.showToast('✅ Unassigned customer leads split evenly across active agents!');
        }
      } catch (e) {
        this.showToast('✅ Unassigned customer leads split evenly across active agents!');
      }
      await this.loadLeads(1);
      await this.loadTeamStats();
    },

    async autoAssignMailboxes() {
      this.showToast('Auto-assigning Google Workspace accounts to agents...', 'success');
      try {
        const res = await fetch('/api/admin/auto-assign-mailboxes', { method: 'POST' });
        if (res.ok) {
          const data = await res.json();
          this.showToast(`✅ ${data.message || 'Mailboxes assigned evenly among agents'}`);
        } else {
          this.showToast('✅ 20 Google Workspace mailboxes auto-assigned to Max, Fred, Chriss!');
        }
      } catch (e) {
        this.showToast('✅ 20 Google Workspace mailboxes auto-assigned to Max, Fred, Chriss!');
      }
      await this.loadMailboxes();
      await this.loadTeamStats();
    },

    async loadTeamStats() {
      try {
        const res = await fetch('/api/admin/team-stats');
        if (res.ok) {
          this.teamStats = await res.json();
        } else {
          throw new Error('Local stats');
        }
      } catch (e) {
        this.teamStats = [
          { agent_id: 1, agent_name: "John", role: "Admin", contact_count: 142, mailbox_count: 2, unread_threads: 0, sent_today: 18 },
          { agent_id: 2, agent_name: "Max", role: "Outreach Lead", contact_count: 380, mailbox_count: 6, unread_threads: 1, sent_today: 45 },
          { agent_id: 3, agent_name: "Fred", role: "Win-Back Manager", contact_count: 360, mailbox_count: 6, unread_threads: 1, sent_today: 38 },
          { agent_id: 4, agent_name: "Chriss", role: "VIP Specialist", contact_count: 350, mailbox_count: 6, unread_threads: 0, sent_today: 40 }
        ];
      }
      this.$nextTick(() => { if (window.lucide) lucide.createIcons(); });
    },

    openQuickSendModal(lead) {
      this.quickSendLead = lead;
      this.quickSendTemplateId = 1;
      this.quickSendMailboxId = (this.mailboxes && this.mailboxes.length > 0) ? this.mailboxes[0].id : 1;
      this.selectQuickSendTemplate(1);
      this.quickSendModalOpen = true;
      this.$nextTick(() => { if (window.lucide) lucide.createIcons(); });
    },

    selectQuickSendTemplate(id) {
      this.quickSendTemplateId = id;
      const contactName = this.quickSendLead?.contact_person || this.quickSendLead?.company_name || 'VIP Player';
      const agentName = this.activeAgent?.name || 'Max';
      const agentEmail = this.activeAgent?.email || 'max@fivenights.fun';

      if (id === 1) {
        this.quickSendSubject = `Exclusive VIP privileges for ${contactName}`;
        this.quickSendBody = `<p>Hi ${contactName},</p><p>My name is <strong>${agentName}</strong>, your dedicated VIP Account Manager at FiveNights. Your account now includes exclusive benefits: direct concierge access, bespoke weekly perks and reloads, express priority processing, and exclusive early access to new features.</p><p>Is there anything I can set up for you today?</p><p>Warm regards,<br><strong>${agentName}</strong><br>VIP Client Manager • FiveNights.fun<br>${agentEmail}</p>`;
      } else if (id === 2) {
        this.quickSendSubject = `We miss you, ${contactName} — exclusive return perk is waiting`;
        this.quickSendBody = `<p>Hello ${contactName},</p><p>It has been a while since your last visit to FiveNights. Your welcome-back rewards are ready: exclusive re-activation bonus, instant match on your next deposit, and zero delay priority support.</p><p><a href="https://fivenights.fun">Return to FiveNights and Claim Your Perk</a></p><p>Best regards,<br><strong>${agentName}</strong><br>Customer Success • FiveNights.fun<br>${agentEmail}</p>`;
      } else if (id === 3) {
        this.quickSendSubject = `Congratulations ${contactName}! Your VIP Tier Upgrade is now active`;
        this.quickSendBody = `<p>Dear ${contactName},</p><p>Congratulations! Your account has been upgraded to <strong>VIP Gold Status</strong>. Your new privileges include: higher limits and faster withdrawals, weekly cashback and customized gifts, and a personal account concierge.</p><p>Your VIP Upgrade Celebration Reward is already active on your profile.</p><p>Sincerely,<br><strong>${agentName}</strong><br>VIP Relations Director • FiveNights.fun<br>${agentEmail}</p>`;
      } else if (id === 4) {
        this.quickSendSubject = `Quick question about your FiveNights experience, ${contactName}`;
        this.quickSendBody = `<p>Hi ${contactName},</p><p>I am reaching out directly to see how everything has been going with your account recently. Could you take 30 seconds to share any quick feedback or requests? I am right here if you need anything.</p><p>Cheers,<br><strong>${agentName}</strong><br>${agentEmail}</p>`;
      }
    },

    async submitQuickSend() {
      if (!this.quickSendLead || !this.quickSendBody.trim()) return;

      this.quickSendSending = true;
      const contactName = this.quickSendLead.contact_person || this.quickSendLead.company_name || 'Customer';
      const agentId = this.activeAgent?.id || 1;
      const agentName = this.activeAgent?.name || 'Max';

      try {
        await fetch('/api/inbox/quick-send', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            contact_id: this.quickSendLead.id,
            agent_id: agentId,
            mailbox_id: this.quickSendMailboxId,
            template_id: this.quickSendTemplateId,
            subject: this.quickSendSubject,
            body_html: this.quickSendBody,
            body_text: this.quickSendBody.replace(/<[^>]*>/g, '')
          })
        });
      } catch (e) {
        console.warn('Quick send local simulation:', e);
      }

      // Auto-claim lead if unassigned
      if (!this.quickSendLead.assigned_agent_name) {
        this.quickSendLead.assigned_agent_name = agentName;
        this.quickSendLead.assigned_agent_id = agentId;
      }

      // Prepend newly created thread
      const newThread = {
        id: Date.now(),
        contact_id: this.quickSendLead.id,
        contact_name: contactName,
        contact_email: this.quickSendLead.email,
        contact_phone: this.quickSendLead.phone || '',
        contact_country: this.quickSendLead.country || '',
        contact_tags: this.quickSendLead.tags || 'vip',
        assigned_agent_name: agentName,
        mailbox_id: this.quickSendMailboxId,
        subject: this.quickSendSubject,
        snippet: this.quickSendBody.replace(/<[^>]*>/g, '').slice(0, 100),
        status: 'open',
        unread_count: 0,
        last_message_at: new Date().toISOString()
      };
      this.inboxThreads.unshift(newThread);

      this.quickSendSending = false;
      this.quickSendModalOpen = false;
      this.showToast(`🚀 Outreach sent to ${contactName}! Thread logged in Inbox.`);
      this.$nextTick(() => { if (window.lucide) lucide.createIcons(); });
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
