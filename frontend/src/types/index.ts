export interface UserProfile {
  id: number;
  full_name: string;
  email: string;
  role: string;
  mfa_enabled?: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface Customer {
  id: number;
  company_name: string;
  contact_person: string;
  email: string;
  phone?: string | null;
  industry?: string | null;
  annual_revenue?: number | null;
  company_size?: number | null;
  current_stage: string;
  health_score: number;
  created_at?: string;
  assigned_sales_rep?: string;
  country?: string;
  notes?: string;
}

export interface CustomerFormData {
  company_name: string;
  contact_person: string;
  email: string;
  phone?: string;
  industry?: string;
  annual_revenue?: number;
  current_stage: string;
  country?: string;
  assigned_sales_rep?: string;
  notes?: string;
}

export interface Meeting {
  id: number;
  customer_id: number;
  title: string;
  transcript?: string | null;
  meeting_date: string;
  summary?: string | null;
  uploaded_file?: string | null;
  created_at?: string;
  customer_name?: string;
  participants?: string;
}

export interface Email {
  id: number;
  customer_id: number;
  subject: string;
  sender: string;
  receiver: string;
  body?: string | null;
  uploaded_file?: string | null;
  created_at?: string;
  customer_name?: string;
  status?: string;
}

export interface SupportTicket {
  id: number;
  customer_id: number;
  ticket_number: string;
  priority: string;
  status: string;
  issue: string;
  resolution?: string | null;
  created_at?: string;
  customer_name?: string;
  assigned_to?: string;
}

export interface Recommendation {
  id: number;
  customer_id: number;
  recommendation: string;
  confidence: number;
  evidence?: string | null;
  status: string;
  approved_by?: number | null;
  reviewer_id?: number | null;
  reviewed_at?: string | null;
  comments?: string | null;
  feedback?: string | null;
  details?: Record<string, unknown> | null;
  created_at?: string;
  company?: string;
  priority?: string;
  roi?: number;
  title?: string;
  business_impact?: string;
  reasoning?: string;
  suggested_action?: string;
}

export interface MemoryEntry {
  id: number;
  customer_id: number;
  memory_type: string;
  memory_data: Record<string, unknown>;
  created_at: string;
}

export interface AuditLog {
  id: number;
  user_id?: number | null;
  action: string;
  entity: string;
  entity_id?: number | null;
  timestamp: string;
  description?: string;
  user_name?: string;
}

export interface Comment {
  id: number;
  recommendation_id: number;
  user_id: number;
  content: string;
  parent_id?: number | null;
  created_at: string;
  entity_type?: string;
  entity_id?: number;
}

export interface KnowledgeDocument {
  id?: number;
  name: string;
  type: string;
  size?: string;
  date?: string;
  category?: string;
  content?: string;
}

export interface DashboardStats {
  total_customers: number;
  active_deals: number;
  pending_recommendations: number;
  completed_recommendations: number;
  total_meetings: number;
  total_tickets: number;
  open_tickets: number;
  total_revenue: number;
  health_score_distribution?: Record<string, number>;
  recent_activities?: AuditLog[];
  projected_revenue?: string;
  total_pipeline?: string;
  pending_actions?: number;
  avg_health?: string;
  total_emails?: number;
  accepted_recommendations?: number;
  open_risks?: number;
}

export interface AgentStep {
  name: string;
  desc: string;
  duration: string;
  confidence: string;
  tokens: number;
  docs: number;
  memory: string;
  retries: number;
  status: 'idle' | 'running' | 'complete' | 'error';
  resultSummary?: string;
}

export interface TimelineItem {
  id: string | number;
  timestamp: string;
  title: string;
  description?: string;
  type: string;
}
