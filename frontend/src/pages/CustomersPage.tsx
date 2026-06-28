import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Search, Filter } from 'lucide-react';
import { toast } from 'sonner';
import { PageHeader } from '../components/ui/PageHeader';
import { Modal, ConfirmDialog } from '../components/ui/Modal';
import { Pagination } from '../components/ui/Pagination';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';
import { CustomerForm } from '../components/forms/CustomerForm';
import { customerService } from '../services/customerService';
import { formatCurrency } from '../lib/utils';
import type { Customer, CustomerFormData } from '../types';

export const CustomersPage = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [industry, setIndustry] = useState('');
  const [stage, setStage] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editCustomer, setEditCustomer] = useState<Customer | null>(null);
  const [deleteId, setDeleteId] = useState<number | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ['customers', page, search, industry, stage],
    queryFn: () => customerService.list({ page, page_size: 10, search, industry: industry || undefined, current_stage: stage || undefined }),
  });

  const createMutation = useMutation({
    mutationFn: (form: CustomerFormData) => customerService.create(form),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['customers'] }); toast.success('Customer created'); setShowForm(false); },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, form }: { id: number; form: CustomerFormData }) => customerService.update(id, form),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['customers'] }); toast.success('Customer updated'); setEditCustomer(null); },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => customerService.remove(id),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['customers'] }); toast.success('Customer deleted'); },
  });

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="Customer Management"
        description="Manage B2B accounts, track health scores, and explore customer intelligence."
        actions={
          <button onClick={() => setShowForm(true)} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-lg flex items-center gap-2">
            <Plus className="h-4 w-4" /> Add Customer
          </button>
        }
      />

      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
          <input value={search} onChange={e => { setSearch(e.target.value); setPage(1); }} placeholder="Search customers..." className="w-full pl-9 pr-4 py-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg text-sm" />
        </div>
        <div className="flex gap-2">
          <select value={industry} onChange={e => { setIndustry(e.target.value); setPage(1); }} className="px-3 py-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg text-sm">
            <option value="">All Industries</option>
            {['Technology', 'Defense', 'Finance', 'Healthcare'].map(i => <option key={i} value={i}>{i}</option>)}
          </select>
          <select value={stage} onChange={e => { setStage(e.target.value); setPage(1); }} className="px-3 py-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg text-sm">
            <option value="">All Stages</option>
            {['prospect', 'qualified', 'proposal', 'negotiation'].map(s => <option key={s} value={s}>{s}</option>)}
          </select>
          <button className="px-3 py-2 border border-gray-200 dark:border-gray-800 rounded-lg text-sm flex items-center gap-1"><Filter className="h-4 w-4" /></button>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl overflow-hidden shadow-sm">
        {isLoading ? <LoadingSkeleton rows={6} /> : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="bg-gray-50 dark:bg-gray-800/50 border-b border-gray-200 dark:border-gray-800 text-xs font-semibold uppercase text-gray-500">
                    <th className="p-4">Customer</th><th className="p-4">Company</th><th className="p-4">Industry</th>
                    <th className="p-4">Deal Stage</th><th className="p-4">ARR</th><th className="p-4">Health</th><th className="p-4">Sales Rep</th><th className="p-4"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                  {(data?.items || []).map(c => (
                    <tr key={c.id} className="hover:bg-gray-50/50 dark:hover:bg-gray-800/30">
                      <td className="p-4"><p className="font-semibold">{c.contact_person}</p><p className="text-xs text-gray-500">{c.email}</p></td>
                      <td className="p-4 font-medium">{c.company_name}</td>
                      <td className="p-4">{c.industry || '—'}</td>
                      <td className="p-4"><span className="px-2 py-0.5 rounded text-xs font-semibold uppercase bg-gray-100 dark:bg-gray-800">{c.current_stage}</span></td>
                      <td className="p-4">{formatCurrency(c.annual_revenue)}</td>
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          <div className="w-14 bg-gray-200 dark:bg-gray-700 h-2 rounded-full"><div className={`h-full rounded-full ${c.health_score > 70 ? 'bg-green-500' : c.health_score > 40 ? 'bg-amber-500' : 'bg-red-500'}`} style={{ width: `${c.health_score}%` }} /></div>
                          <span className="text-xs font-semibold">{c.health_score}%</span>
                        </div>
                      </td>
                      <td className="p-4 text-xs">{c.assigned_sales_rep || 'Unassigned'}</td>
                      <td className="p-4 text-right space-x-2 whitespace-nowrap">
                        <button onClick={() => navigate(`/customers/${c.id}`)} className="text-blue-600 text-xs font-semibold">View</button>
                        <button onClick={() => setEditCustomer(c)} className="text-gray-600 text-xs font-semibold">Edit</button>
                        <button onClick={() => setDeleteId(c.id)} className="text-red-600 text-xs font-semibold">Delete</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <Pagination page={data?.page || 1} totalPages={data?.total_pages || 1} onPageChange={setPage} />
          </>
        )}
      </div>

      <Modal open={showForm} onClose={() => setShowForm(false)} title="Add Customer" size="lg">
        <CustomerForm onCancel={() => setShowForm(false)} onSubmit={d => createMutation.mutate(d)} loading={createMutation.isPending} />
      </Modal>

      <Modal open={!!editCustomer} onClose={() => setEditCustomer(null)} title="Edit Customer" size="lg">
        {editCustomer && (
          <CustomerForm
            defaultValues={editCustomer as any}
            onCancel={() => setEditCustomer(null)}
            onSubmit={d => updateMutation.mutate({ id: editCustomer.id, form: d })}
            loading={updateMutation.isPending}
          />
        )}
      </Modal>

      <ConfirmDialog open={deleteId !== null} onClose={() => setDeleteId(null)} onConfirm={() => deleteId && deleteMutation.mutate(deleteId)} title="Delete Customer" message="Are you sure you want to delete this customer? This action cannot be undone." confirmLabel="Delete" destructive />
    </div>
  );
};
