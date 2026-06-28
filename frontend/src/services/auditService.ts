import { apiGet } from '../lib/api';
import { MOCK_AUDIT_LOGS } from '../lib/mockData';
import type { AuditLog } from '../types';

export const auditService = {
  async list(): Promise<AuditLog[]> {
    try {
      const data = await apiGet<AuditLog[] | { items: AuditLog[] }>('/audit-logs');
      return Array.isArray(data) ? data : data.items || [];
    } catch {
      return MOCK_AUDIT_LOGS;
    }
  },

  async getRecent(): Promise<AuditLog[]> {
    try {
      return await apiGet<AuditLog[]>('/audit-logs/recent');
    } catch {
      return MOCK_AUDIT_LOGS;
    }
  },
};
