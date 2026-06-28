import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus } from 'lucide-react';
import { toast } from 'sonner';
import { PageHeader } from '../components/ui/PageHeader';
import { Modal, ConfirmDialog } from '../components/ui/Modal';
import { MeetingCard } from '../components/cards/MeetingCard';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';
import { meetingService } from '../services/meetingService';
import { customerService } from '../services/customerService';
import type { Meeting } from '../types';

export const MeetingsPage = () => {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [editMeeting, setEditMeeting] = useState<Meeting | null>(null);
  const [viewMeeting, setViewMeeting] = useState<Meeting | null>(null);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [form, setForm] = useState({ customer_id: 1, title: '', meeting_date: '', participants: '', summary: '', transcript: '' });

  const { data: meetings, isLoading } = useQuery({ queryKey: ['meetings'], queryFn: () => meetingService.list() });
  const { data: customers } = useQuery({ queryKey: ['customers-all'], queryFn: () => customerService.list({ page_size: 100 }) });

  const saveMutation = useMutation({
    mutationFn: async () => {
      const payload = {
        customer_id: Number(form.customer_id),
        title: form.title,
        meeting_date: form.meeting_date || new Date().toISOString(),
        summary: form.summary,
        transcript: form.transcript,
        participants: form.participants,
        customer_name: customers?.items.find(c => c.id === Number(form.customer_id))?.company_name,
      };
      if (editMeeting) return meetingService.update(editMeeting.id, payload);
      return meetingService.create(payload as Omit<Meeting, 'id'>);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['meetings'] });
      toast.success(editMeeting ? 'Meeting updated' : 'Meeting saved — AI recommendation generation triggered');
      setShowForm(false);
      setEditMeeting(null);
      setForm({ customer_id: 1, title: '', meeting_date: '', participants: '', summary: '', transcript: '' });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => meetingService.remove(id),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['meetings'] }); toast.success('Meeting deleted'); },
  });

  const openEdit = (m: Meeting) => {
    setEditMeeting(m);
    setForm({ customer_id: m.customer_id, title: m.title, meeting_date: m.meeting_date?.slice(0, 16) || '', participants: m.participants || '', summary: m.summary || '', transcript: m.transcript || '' });
    setShowForm(true);
  };

  const inputClass = 'w-full p-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-800 rounded-lg text-sm';

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader title="Meetings" description="Manage meeting transcripts and trigger AI analysis." actions={
        <button onClick={() => { setEditMeeting(null); setShowForm(true); }} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-lg flex items-center gap-2"><Plus className="h-4 w-4" /> New Meeting</button>
      } />

      {isLoading ? <LoadingSkeleton /> : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {(meetings || []).map(m => (
            <MeetingCard key={m.id} meeting={m} onView={() => setViewMeeting(m)} onEdit={() => openEdit(m)} onDelete={() => setDeleteId(m.id)} />
          ))}
        </div>
      )}

      <Modal open={showForm} onClose={() => { setShowForm(false); setEditMeeting(null); }} title={editMeeting ? 'Edit Meeting' : 'New Meeting'} size="lg">
        <div className="space-y-4">
          <div><label className="text-xs font-bold text-gray-500 uppercase">Customer</label>
            <select value={form.customer_id} onChange={e => setForm({ ...form, customer_id: Number(e.target.value) })} className={inputClass}>
              {(customers?.items || []).map(c => <option key={c.id} value={c.id}>{c.company_name}</option>)}
            </select>
          </div>
          <div><label className="text-xs font-bold text-gray-500 uppercase">Title *</label><input value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} className={inputClass} required /></div>
          <div><label className="text-xs font-bold text-gray-500 uppercase">Date *</label><input type="datetime-local" value={form.meeting_date} onChange={e => setForm({ ...form, meeting_date: e.target.value })} className={inputClass} required /></div>
          <div><label className="text-xs font-bold text-gray-500 uppercase">Participants</label><input value={form.participants} onChange={e => setForm({ ...form, participants: e.target.value })} className={inputClass} /></div>
          <div><label className="text-xs font-bold text-gray-500 uppercase">Summary</label><textarea value={form.summary} onChange={e => setForm({ ...form, summary: e.target.value })} rows={2} className={inputClass} /></div>
          <div><label className="text-xs font-bold text-gray-500 uppercase">Transcript</label><textarea value={form.transcript} onChange={e => setForm({ ...form, transcript: e.target.value })} rows={6} className={inputClass} placeholder="Paste full meeting transcript..." /></div>
          <div className="flex justify-end gap-2">
            <button onClick={() => setShowForm(false)} className="px-4 py-2 text-sm text-gray-600 rounded-lg hover:bg-gray-100">Cancel</button>
            <button onClick={() => form.title && saveMutation.mutate()} disabled={!form.title || saveMutation.isPending} className="px-4 py-2 bg-blue-600 text-white text-sm font-semibold rounded-lg disabled:opacity-50">Save</button>
          </div>
        </div>
      </Modal>

      <Modal open={!!viewMeeting} onClose={() => setViewMeeting(null)} title={viewMeeting?.title || 'Meeting'} size="lg">
        {viewMeeting && (
          <div className="space-y-3 text-sm">
            <p><b>Date:</b> {viewMeeting.meeting_date}</p>
            <p><b>Summary:</b> {viewMeeting.summary}</p>
            <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg max-h-64 overflow-y-auto whitespace-pre-wrap">{viewMeeting.transcript || 'No transcript'}</div>
          </div>
        )}
      </Modal>

      <ConfirmDialog open={deleteId !== null} onClose={() => setDeleteId(null)} onConfirm={() => deleteId && deleteMutation.mutate(deleteId)} title="Delete Meeting" message="Delete this meeting permanently?" confirmLabel="Delete" destructive />
    </div>
  );
};
