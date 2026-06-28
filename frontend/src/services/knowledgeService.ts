import { apiGet, apiPost } from '../lib/api';
import { MOCK_KNOWLEDGE } from '../lib/mockData';
import type { KnowledgeDocument } from '../types';

export const knowledgeService = {
  async list(): Promise<KnowledgeDocument[]> {
    try {
      const data = await apiGet<KnowledgeDocument[] | { items: KnowledgeDocument[] }>('/knowledge/documents');
      return Array.isArray(data) ? data : data.items || [];
    } catch {
      return MOCK_KNOWLEDGE;
    }
  },

  async search(query: string): Promise<KnowledgeDocument[]> {
    try {
      const data = await apiPost<{ results: KnowledgeDocument[] }>('/knowledge/search', { query });
      return data.results || [];
    } catch {
      const q = query.toLowerCase();
      return MOCK_KNOWLEDGE.filter(d => d.name.toLowerCase().includes(q) || d.content?.toLowerCase().includes(q));
    }
  },

  async upload(_file: File): Promise<void> {
    try {
      const formData = new FormData();
      formData.append('file', _file);
      await fetch(`${import.meta.env.VITE_API_BASE_URL || '/api/v1'}/knowledge/upload`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${localStorage.getItem('token') || ''}` },
        body: formData,
      });
    } catch {
      // demo fallback
    }
  },
};
