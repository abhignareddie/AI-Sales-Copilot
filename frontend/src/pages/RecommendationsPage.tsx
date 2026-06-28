import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { PageHeader } from '../components/ui/PageHeader';
import { Modal } from '../components/ui/Modal';
import { RecommendationCard } from '../components/cards/RecommendationCard';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';
import { recommendationService } from '../services/recommendationService';

export const RecommendationsPage = () => {
  const queryClient = useQueryClient();
  const [feedbackId, setFeedbackId] = useState<number | null>(null);
  const [feedbackText, setFeedbackText] = useState('');

  const { data: recs, isLoading } = useQuery({ queryKey: ['recommendations'], queryFn: () => recommendationService.list() });

  const actionMutation = useMutation({
    mutationFn: ({ id, action, feedback }: { id: number; action: 'approve' | 'reject'; feedback?: string }) =>
      action === 'approve' ? recommendationService.approve(id, feedback) : recommendationService.reject(id, feedback),
    onSuccess: (_, vars) => {
      queryClient.invalidateQueries({ queryKey: ['recommendations'] });
      toast.success(`Recommendation ${vars.action === 'approve' ? 'accepted' : 'rejected'} — audit log updated`);
    },
  });

  const feedbackMutation = useMutation({
    mutationFn: ({ id, text }: { id: number; text: string }) => recommendationService.addFeedback(id, text),
    onSuccess: () => { toast.success('Feedback submitted'); setFeedbackId(null); setFeedbackText(''); },
  });

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader title="Recommendation Center" description="Review AI-generated next best actions with full explainability." />

      {isLoading ? <LoadingSkeleton rows={4} /> : (
        <div className="space-y-4">
          {(recs || []).map(rec => (
            <RecommendationCard
              key={rec.id}
              rec={rec}
              onAccept={() => actionMutation.mutate({ id: rec.id, action: 'approve' })}
              onReject={() => actionMutation.mutate({ id: rec.id, action: 'reject' })}
              onFeedback={() => setFeedbackId(rec.id)}
            />
          ))}
        </div>
      )}

      <Modal open={feedbackId !== null} onClose={() => setFeedbackId(null)} title="Submit Feedback" size="md">
        <textarea value={feedbackText} onChange={e => setFeedbackText(e.target.value)} rows={4} className="w-full p-3 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-800 rounded-lg text-sm mb-4" placeholder="Share feedback on this recommendation..." />
        <div className="flex justify-end gap-2">
          <button onClick={() => setFeedbackId(null)} className="px-4 py-2 text-sm text-gray-600 rounded-lg">Cancel</button>
          <button onClick={() => feedbackId && feedbackMutation.mutate({ id: feedbackId, text: feedbackText })} className="px-4 py-2 bg-blue-600 text-white text-sm font-semibold rounded-lg">Submit</button>
        </div>
      </Modal>
    </div>
  );
};
