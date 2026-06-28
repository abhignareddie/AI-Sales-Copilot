import { apiDelete, apiGet, apiPost, apiPut } from '../lib/api';
import { MOCK_TICKETS } from '../lib/mockData';
import type { SupportTicket } from '../types';

export const ticketService = {
  async list(): Promise<SupportTicket[]> {
    try {
      const data = await apiGet<SupportTicket[] | { items: SupportTicket[] }>('/support-tickets');
      return Array.isArray(data) ? data : data.items || [];
    } catch {
      return MOCK_TICKETS;
    }
  },

  async create(data: Omit<SupportTicket, 'id'>): Promise<SupportTicket> {
    try {
      return await apiPost<SupportTicket>('/support-tickets', {
        customer_id: data.customer_id,
        ticket_number: data.ticket_number || `TKT-${Date.now()}`,
        priority: data.priority,
        status: data.status,
        issue: data.issue,
        resolution: data.resolution,
      });
    } catch {
      return { id: Date.now(), ...data, ticket_number: data.ticket_number || `TKT-${Date.now()}` };
    }
  },

  async update(id: number, data: Partial<SupportTicket>): Promise<SupportTicket> {
    try {
      return await apiPut<SupportTicket>(`/support-tickets/${id}`, data);
    } catch {
      const existing = MOCK_TICKETS.find(t => t.id === id) || MOCK_TICKETS[0];
      return { ...existing, ...data };
    }
  },

  async remove(id: number): Promise<void> {
    try {
      await apiDelete(`/support-tickets/${id}`);
    } catch {
      // demo fallback
    }
  },
};
