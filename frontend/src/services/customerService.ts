import { apiDelete, apiGet, apiPost, apiPut } from '../lib/api';
import { MOCK_CUSTOMERS } from '../lib/mockData';
import type { Customer, CustomerFormData, PaginatedResponse } from '../types';

export interface CustomerFilters {
  page?: number;
  page_size?: number;
  industry?: string;
  current_stage?: string;
  search?: string;
}

export const customerService = {
  async list(filters: CustomerFilters = {}): Promise<PaginatedResponse<Customer>> {
    const params = new URLSearchParams();
    if (filters.page) params.set('page', String(filters.page));
    if (filters.page_size) params.set('page_size', String(filters.page_size));
    if (filters.industry) params.set('industry', filters.industry);
    if (filters.current_stage) params.set('current_stage', filters.current_stage);
    const query = params.toString();
    try {
      const data = await apiGet<PaginatedResponse<Customer>>(`/customers${query ? `?${query}` : ''}`);
      let items = data.items || [];
      if (filters.search) {
        const q = filters.search.toLowerCase();
        items = items.filter(c =>
          c.company_name.toLowerCase().includes(q) ||
          c.contact_person.toLowerCase().includes(q) ||
          c.email.toLowerCase().includes(q),
        );
      }
      return { ...data, items };
    } catch {
      let items = [...MOCK_CUSTOMERS];
      if (filters.search) {
        const q = filters.search.toLowerCase();
        items = items.filter(c =>
          c.company_name.toLowerCase().includes(q) ||
          c.contact_person.toLowerCase().includes(q),
        );
      }
      if (filters.industry) items = items.filter(c => c.industry === filters.industry);
      if (filters.current_stage) items = items.filter(c => c.current_stage === filters.current_stage);
      const page = filters.page || 1;
      const pageSize = filters.page_size || 10;
      const start = (page - 1) * pageSize;
      return {
        items: items.slice(start, start + pageSize),
        total: items.length,
        page,
        page_size: pageSize,
        total_pages: Math.ceil(items.length / pageSize) || 1,
      };
    }
  },

  async get(id: number): Promise<Customer> {
    try {
      return await apiGet<Customer>(`/customers/${id}`);
    } catch {
      const found = MOCK_CUSTOMERS.find(c => c.id === id);
      if (!found) throw new Error('Customer not found');
      return found;
    }
  },

  async create(data: CustomerFormData): Promise<Customer> {
    const payload = {
      company_name: data.company_name,
      contact_person: data.contact_person,
      email: data.email,
      phone: data.phone,
      industry: data.industry,
      annual_revenue: data.annual_revenue,
      current_stage: data.current_stage || 'prospect',
      health_score: 50,
    };
    try {
      return await apiPost<Customer>('/customers', payload);
    } catch {
      return { id: Date.now(), ...payload, health_score: 50, assigned_sales_rep: data.assigned_sales_rep, country: data.country, notes: data.notes };
    }
  },

  async update(id: number, data: Partial<CustomerFormData>): Promise<Customer> {
    try {
      return await apiPut<Customer>(`/customers/${id}`, data);
    } catch {
      const existing = MOCK_CUSTOMERS.find(c => c.id === id) || MOCK_CUSTOMERS[0];
      return { ...existing, ...data };
    }
  },

  async remove(id: number): Promise<void> {
    try {
      await apiDelete(`/customers/${id}`);
    } catch {
      // demo fallback — no-op
    }
  },
};
