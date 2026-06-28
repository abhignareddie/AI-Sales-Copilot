import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus } from 'lucide-react';
import { toast } from 'sonner';
import { PageHeader } from '../components/ui/PageHeader';
import { Modal, ConfirmDialog } from '../components/ui/Modal';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';
import { getPriorityStyle, getStatusStyle, formatDate } from '../lib/utils';
import { ticketService } from '../services/ticketService';
import { customerService } from '../services/customerService';
import type { SupportTicket } from '../types';

export const SupportTicketsPage = () => {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [editTicket, setEditTicket] = useState<SupportTicket | null>(null);
  const [viewTicket, setViewTicket] = useState<SupportTicket | null>(null);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [form, setForm] = useState({ customer_id: 1, priority: 'medium', status: 'open', issue: '', assigned_to: '' });

  const { data: tickets, isLoading } = useQuery({ queryKey: ['tickets'], queryFn: () => ticketService.list() });
  const { data: customers } = useQuery({ queryKey: ['customers-all'], queryFn: () => customerService.list({ page_size: 100 }) });

  const saveMutation = useMutation({
    mutationFn: async () => {
      const payload = { ...form, customer_id: Number(form.customer_id), ticket_number: `TKT-${Date.now()}`, customer_name: customers?.items.find(c => c.id === Number(form.customer_id))?.company_name };
      if (editTicket) return ticketService.update(editTicket.id, payload);
      return ticketService.create(payload as Omit<SupportTicket, 'id'>);
    },
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['tickets'] }); toast.success('Ticket saved'); setShowForm(false); setEditTicket(null); },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => ticketService.remove(id),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['tickets'] }); toast.success('Ticket deleted'); },
  });

  const inputClass = 'w-full p-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-800 rounded-lg text-sm';

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader title="Support Tickets" description="Track and resolve customer support issues." actions={
        <button onClick={() => setShowForm(true)} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-lg flex items-center gap-2"><Plus className="h-4 w-4" /> New Ticket</button>
      } />

      <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl shadow-sm overflow-hidden">
        {isLoading ? <LoadingSkeleton /> : (
          <table className="w-full text-sm text-left">
            <thead><tr className="bg-gray-50 dark:bg-gray-800/50 text-xs uppercase text-gray-500"><th className="p-4">Priority</th><th className="p-4">Status</th><th className="p-4">Issue</th><th className="p-4">Customer</th><th className="p-4">Assigned To</th><th className="p-4">Created</th><th className="p-4"></th></tr></thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
              {(tickets || []).map(t => (
                <tr key={t.id} className="hover:bg-gray-50/50 dark:hover:bg-gray-800/30">
                  <td className="p-4"><span className={getPriorityStyle(t.priority)}>{t.priority}</span></td>
                  <td className="p-4"><span className={getStatusStyle(t.status)}>{t.status}</span></td>
                  <td className="p-4 font-medium">{t.issue}</td>
                  <td className="p-4">{t.customer_name || `#${t.customer_id}`}</td>
                  <td className="p-4">{t.assigned_to || 'Unassigned'}</td>
                  <td className="p-4">{formatDate(t.created_at)}</td>
                  <td className="p-4 text-right space-x-2">
                    <button onClick={() => setViewTicket(t)} className="text-xs font-semibold text-blue-600">View</button>
                    <button onClick={() => { setEditTicket(t); setForm({ customer_id: t.customer_id, priority: t.priority, status: t.status, issue: t.issue, assigned_to: t.assigned_to || '' }); setShowForm(true); }} className="text-xs font-semibold text-gray-600">Edit</button>
                    <button onClick={() => setDeleteId(t.id)} className="text-xs font-semibold text-red-600">Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <Modal open={showForm} onClose={() => { setShowForm(false); setEditTicket(null); }} title={editTicket ? 'Edit Ticket' : 'New Ticket'} size="md">
        <div className="space-y-4">
          <select value={form.customer_id} onChange={e => setForm({ ...form, customer_id: Number(e.target.value) })} className={inputClass}>{(customers?.items || []).map(c => <option key={c.id} value={c.id}>{c.company_name}</option>)}</select>
          <select value={form.priority} onChange={e => setForm({ ...form, priority: e.target.value })} className={inputClass}><option value="high">High</option><option value="medium">Medium</option><option value="low">Low</option></select>
          <select value={form.status} onChange={e => setForm({ ...form, status: e.target.value })} className={inputClass}><option value="open">Open</option><option value="in_progress">In Progress</option><option value="closed">Closed</option></select>
          <textarea placeholder="Issue description *" value={form.issue} onChange={e => setForm({ ...form, issue: e.target.value })} rows={3} className={inputClass} />
          <input placeholder="Assigned To" value={form.assigned_to} onChange={e => setForm({ ...form, assigned_to: e.target.value })} className={inputClass} />
          <div className="flex justify-end gap-2">
            <button onClick={() => setShowForm(false)} className="px-4 py-2 text-sm text-gray-600 rounded-lg">Cancel</button>
            <button onClick={() => form.issue && saveMutation.mutate()} className="px-4 py-2 bg-blue-600 text-white text-sm font-semibold rounded-lg">Save</button>
          </div>
        </div>
      </Modal>

      <Modal open={!!viewTicket} onClose={() => setViewTicket(null)} title={`Ticket ${viewTicket?.ticket_number || 'Details'}`} size="md">
        {viewTicket && (
          <div className="space-y-3 text-sm">
            <p><b>Priority:</b> <span className={getPriorityStyle(viewTicket.priority)}>{viewTicket.priority}</span></p>
            <p><b>Status:</b> <span className={getStatusStyle(viewTicket.status)}>{viewTicket.status}</span></p>
            <p><b>Assigned To:</b> {viewTicket.assigned_to || 'Unassigned'}</p>
            <p><b>Created At:</b> {formatDate(viewTicket.created_at)}</p>
            <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg max-h-64 overflow-y-auto whitespace-pre-wrap"><b>Issue:</b><br />{viewTicket.issue}</div>
          </div>
        )}
      </Modal>

      <ConfirmDialog open={deleteId !== null} onClose={() => setDeleteId(null)} onConfirm={() => deleteId && deleteMutation.mutate(deleteId)} title="Delete Ticket" message="Delete this support ticket?" confirmLabel="Delete" destructive />
    </div>
  );
};
