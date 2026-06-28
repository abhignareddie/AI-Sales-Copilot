import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus } from 'lucide-react';
import { toast } from 'sonner';
import { PageHeader } from '../components/ui/PageHeader';
import { Modal, ConfirmDialog } from '../components/ui/Modal';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';
import { getStatusStyle, formatDate } from '../lib/utils';
import { emailService } from '../services/emailService';
import { customerService } from '../services/customerService';
import type { Email } from '../types';

export const EmailsPage = () => {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [editEmail, setEditEmail] = useState<Email | null>(null);
  const [viewEmail, setViewEmail] = useState<Email | null>(null);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [form, setForm] = useState({ customer_id: 1, subject: '', sender: '', receiver: '', body: '' });

  const { data: emails, isLoading } = useQuery({ queryKey: ['emails'], queryFn: () => emailService.list() });
  const { data: customers } = useQuery({ queryKey: ['customers-all'], queryFn: () => customerService.list({ page_size: 100 }) });

  const saveMutation = useMutation({
    mutationFn: async () => {
      const payload = { ...form, customer_id: Number(form.customer_id), status: 'sent' };
      if (editEmail) return emailService.update(editEmail.id, payload);
      return emailService.create(payload);
    },
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['emails'] }); toast.success('Email saved'); setShowForm(false); setEditEmail(null); },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => emailService.remove(id),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['emails'] }); toast.success('Email deleted'); },
  });

  const inputClass = 'w-full p-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-800 rounded-lg text-sm';

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader title="Emails" description="Track customer email communications." actions={
        <button onClick={() => setShowForm(true)} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-lg flex items-center gap-2"><Plus className="h-4 w-4" /> Add Email</button>
      } />

      <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl shadow-sm overflow-hidden">
        {isLoading ? <LoadingSkeleton /> : (
          <table className="w-full text-sm text-left">
            <thead><tr className="bg-gray-50 dark:bg-gray-800/50 text-xs uppercase text-gray-500"><th className="p-4">Subject</th><th className="p-4">From</th><th className="p-4">To</th><th className="p-4">Customer</th><th className="p-4">Date</th><th className="p-4">Status</th><th className="p-4"></th></tr></thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
              {(emails || []).map(e => (
                <tr key={e.id} className="hover:bg-gray-50/50 dark:hover:bg-gray-800/30">
                  <td className="p-4 font-semibold">{e.subject}</td>
                  <td className="p-4">{e.sender}</td>
                  <td className="p-4">{e.receiver}</td>
                  <td className="p-4">{e.customer_name || `#${e.customer_id}`}</td>
                  <td className="p-4">{formatDate(e.created_at)}</td>
                  <td className="p-4"><span className={getStatusStyle(e.status || 'sent')}>{e.status || 'sent'}</span></td>
                  <td className="p-4 text-right space-x-2">
                    <button onClick={() => setViewEmail(e)} className="text-xs font-semibold text-blue-600">View</button>
                    <button onClick={() => { setEditEmail(e); setForm({ customer_id: e.customer_id, subject: e.subject, sender: e.sender, receiver: e.receiver, body: e.body || '' }); setShowForm(true); }} className="text-xs font-semibold text-gray-600">Edit</button>
                    <button onClick={() => setDeleteId(e.id)} className="text-xs font-semibold text-red-600">Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <Modal open={showForm} onClose={() => { setShowForm(false); setEditEmail(null); }} title={editEmail ? 'Edit Email' : 'Add Email'} size="lg">
        <div className="space-y-4">
          <select value={form.customer_id} onChange={e => setForm({ ...form, customer_id: Number(e.target.value) })} className={inputClass}>
            {(customers?.items || []).map(c => <option key={c.id} value={c.id}>{c.company_name}</option>)}
          </select>
          <input placeholder="Subject *" value={form.subject} onChange={e => setForm({ ...form, subject: e.target.value })} className={inputClass} />
          <input placeholder="From *" value={form.sender} onChange={e => setForm({ ...form, sender: e.target.value })} className={inputClass} />
          <input placeholder="To *" value={form.receiver} onChange={e => setForm({ ...form, receiver: e.target.value })} className={inputClass} />
          <textarea placeholder="Body" value={form.body} onChange={e => setForm({ ...form, body: e.target.value })} rows={6} className={inputClass} />
          <div className="border-2 border-dashed border-gray-200 dark:border-gray-700 rounded-lg p-4 text-center text-xs text-gray-400">Attachments (optional) — drag & drop UI</div>
          <div className="flex justify-end gap-2">
            <button onClick={() => setShowForm(false)} className="px-4 py-2 text-sm text-gray-600 rounded-lg">Cancel</button>
            <button onClick={() => form.subject && form.sender && form.receiver && saveMutation.mutate()} className="px-4 py-2 bg-blue-600 text-white text-sm font-semibold rounded-lg">Save</button>
          </div>
        </div>
      </Modal>

      <Modal open={!!viewEmail} onClose={() => setViewEmail(null)} title={viewEmail?.subject || 'Email Details'} size="lg">
        {viewEmail && (
          <div className="space-y-3 text-sm">
            <p><b>From:</b> {viewEmail.sender}</p>
            <p><b>To:</b> {viewEmail.receiver}</p>
            <p><b>Date:</b> {formatDate(viewEmail.created_at)}</p>
            <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg max-h-96 overflow-y-auto whitespace-pre-wrap">{viewEmail.body || 'No body content'}</div>
          </div>
        )}
      </Modal>

      <ConfirmDialog open={deleteId !== null} onClose={() => setDeleteId(null)} onConfirm={() => deleteId && deleteMutation.mutate(deleteId)} title="Delete Email" message="Delete this email?" confirmLabel="Delete" destructive />
    </div>
  );
};
