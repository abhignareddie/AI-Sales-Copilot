import type { Customer, Recommendation, Meeting, Email, SupportTicket, AuditLog, MemoryEntry, KnowledgeDocument } from '../types';

export const MOCK_CUSTOMERS: Customer[] = [
  { id: 1, company_name: 'Acme Corporation', contact_person: 'John Doe', email: 'john@acme.com', phone: '+1-555-0101', industry: 'Technology', annual_revenue: 150000, company_size: 1200, current_stage: 'proposal', health_score: 45, assigned_sales_rep: 'Sarah Chen', country: 'USA' },
  { id: 2, company_name: 'Stark Industries', contact_person: 'Tony Stark', email: 'tony@stark.com', phone: '+1-555-0102', industry: 'Defense', annual_revenue: 850000, company_size: 4500, current_stage: 'negotiation', health_score: 82, assigned_sales_rep: 'Mike Ross', country: 'USA' },
  { id: 3, company_name: 'Wayne Enterprises', contact_person: 'Bruce Wayne', email: 'bruce@wayne.com', phone: '+1-555-0103', industry: 'Finance', annual_revenue: 620000, company_size: 3200, current_stage: 'qualified', health_score: 59, assigned_sales_rep: 'Sarah Chen', country: 'USA' },
];

export const MOCK_RECOMMENDATIONS: Recommendation[] = [
  { id: 1, customer_id: 1, company: 'Acme Corporation', recommendation: 'Schedule immediate VP proposal alignment review', confidence: 0.88, priority: 'high', roi: 15000, status: 'Pending Review', evidence: 'Deal size is above $100K threshold, and health score has dropped under 50.', title: 'VP Proposal Alignment', business_impact: 'Protect $150K ARR deal', reasoning: 'Health score decline + open support tickets indicate escalation risk.', suggested_action: 'Schedule VP alignment call within 48 hours' },
  { id: 2, customer_id: 3, company: 'Wayne Enterprises', recommendation: 'Schedule technical deep-dive demo highlighting multi-cloud support', confidence: 0.76, priority: 'medium', roi: 8000, status: 'Pending Review', evidence: 'Competitor presence detected in customer emails.', title: 'Technical Deep-Dive Demo', business_impact: 'Differentiate against competitor', reasoning: 'Email sentiment analysis flagged competitor evaluation.', suggested_action: 'Book 90-min technical demo with solutions architect' },
];

export const MOCK_MEETINGS: Meeting[] = [
  { id: 1, customer_id: 1, title: 'Q2 Business Review', meeting_date: '2026-06-20T14:00:00', summary: 'Discussed renewal timeline and SSO requirements.', transcript: 'Customer expressed concerns about SSO integration timeline...', customer_name: 'Acme Corporation', participants: 'John Doe, Sarah Chen' },
  { id: 2, customer_id: 2, title: 'Technical Discovery', meeting_date: '2026-06-22T10:00:00', summary: 'Reviewed architecture and deployment options.', transcript: 'Tony outlined requirements for on-prem deployment...', customer_name: 'Stark Industries', participants: 'Tony Stark, Mike Ross' },
];

export const MOCK_EMAILS: Email[] = [
  { id: 1, customer_id: 1, subject: 'SSO Integration Timeline', sender: 'john@acme.com', receiver: 'sales@company.com', body: 'We need SSO live before Q3...', created_at: '2026-06-21T09:00:00', customer_name: 'Acme Corporation', status: 'received' },
  { id: 2, customer_id: 3, subject: 'Competitor Evaluation', sender: 'bruce@wayne.com', receiver: 'sales@company.com', body: 'We are evaluating Gong alongside your platform...', created_at: '2026-06-23T11:30:00', customer_name: 'Wayne Enterprises', status: 'received' },
];

export const MOCK_TICKETS: SupportTicket[] = [
  { id: 1, customer_id: 1, ticket_number: 'TKT-1001', priority: 'high', status: 'open', issue: 'SSO login failures for enterprise users', created_at: '2026-06-19T08:00:00', customer_name: 'Acme Corporation', assigned_to: 'Support Team A' },
  { id: 2, customer_id: 2, ticket_number: 'TKT-1002', priority: 'medium', status: 'in_progress', issue: 'API rate limit configuration request', created_at: '2026-06-20T14:00:00', customer_name: 'Stark Industries', assigned_to: 'Support Team B' },
];

export const MOCK_AUDIT_LOGS: AuditLog[] = [
  { id: 1, user_id: 1, action: 'approve', entity: 'recommendation', entity_id: 5, timestamp: '2026-06-26T10:30:00', description: 'Approved recommendation #5 for Acme Corporation', user_name: 'Sarah Chen' },
  { id: 2, user_id: 2, action: 'create', entity: 'meeting', entity_id: 12, timestamp: '2026-06-26T09:15:00', description: 'Created meeting transcript for Stark Industries', user_name: 'Mike Ross' },
  { id: 3, user_id: 1, action: 'reject', entity: 'recommendation', entity_id: 3, timestamp: '2026-06-25T16:45:00', description: 'Rejected discount recommendation — insufficient margin', user_name: 'Sarah Chen' },
];

export const MOCK_MEMORY: MemoryEntry[] = [
  { id: 1, customer_id: 1, memory_type: 'preference', memory_data: { note: 'Prefers Slack channel updates over email' }, created_at: '2026-06-15T10:00:00' },
  { id: 2, customer_id: 1, memory_type: 'interaction', memory_data: { type: 'meeting', title: 'Q2 Business Review' }, created_at: '2026-06-20T14:00:00' },
];

export const MOCK_KNOWLEDGE: KnowledgeDocument[] = [
  { id: 1, name: 'Enterprise Sales Playbook', type: 'PDF', size: '2.4 MB', date: '2026-06-24', category: 'playbooks', content: 'Step-by-step enterprise sales methodology...' },
  { id: 2, name: 'Premium Pricing Plan', type: 'PDF', size: '1.2 MB', date: '2026-06-25', category: 'product_docs', content: 'Pricing tiers and discount guidelines...' },
  { id: 3, name: 'Objection Handling Best Practices', type: 'DOCX', size: '890 KB', date: '2026-06-20', category: 'best_practices', content: 'Common objections and proven responses...' },
  { id: 4, name: 'Security & Compliance FAQ', type: 'PDF', size: '450 KB', date: '2026-06-18', category: 'faqs', content: 'SOC2, GDPR, and data residency answers...' },
  { id: 5, name: 'Discount Approval Policy', type: 'PDF', size: '320 KB', date: '2026-06-10', category: 'policies', content: 'Maximum discount thresholds by deal size...' },
];

export const DEFAULT_DASHBOARD_STATS = {
  total_customers: 3,
  active_deals: 3,
  pending_recommendations: 2,
  completed_recommendations: 8,
  total_meetings: 12,
  total_tickets: 5,
  open_tickets: 2,
  total_revenue: 1620000,
  total_emails: 24,
  accepted_recommendations: 8,
  open_risks: 3,
  projected_revenue: '$128,500',
  total_pipeline: '$1.45M',
  pending_actions: 3,
  avg_health: '62.5%',
};
