import { apiPost } from '../lib/api';
import type { Comment } from '../types';

const localComments: Comment[] = [];

export const commentService = {
  async listForRecommendation(recommendationId: number): Promise<Comment[]> {
    try {
      const res = await apiPost<Comment[]>('/review/comment', { recommendation_id: recommendationId });
      return res;
    } catch {
      return localComments.filter(c => c.recommendation_id === recommendationId);
    }
  },

  async create(recommendationId: number, content: string): Promise<Comment> {
    try {
      return await apiPost<Comment>('/review/comment', { recommendation_id: recommendationId, content });
    } catch {
      const comment: Comment = {
        id: Date.now(),
        recommendation_id: recommendationId,
        user_id: 1,
        content,
        created_at: new Date().toISOString(),
      };
      localComments.push(comment);
      return comment;
    }
  },
};
