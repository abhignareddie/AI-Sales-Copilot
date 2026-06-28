import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import { formatCurrency } from '../../lib/utils';
import type { Customer } from '../../types';

interface CustomerCardProps {
  customer: Customer;
  onEdit?: () => void;
  onDelete?: () => void;
}

export const CustomerCard = ({ customer, onEdit, onDelete }: CustomerCardProps) => (
  <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-4 shadow-sm hover:shadow-md transition">
    <div className="flex items-start justify-between mb-3">
      <div>
        <h3 className="font-bold text-gray-900 dark:text-gray-100">{customer.company_name}</h3>
        <p className="text-sm text-gray-500">{customer.contact_person}</p>
      </div>
      <span className="px-2 py-0.5 rounded text-xs font-semibold uppercase bg-gray-100 dark:bg-gray-800">{customer.current_stage}</span>
    </div>
    <div className="grid grid-cols-2 gap-2 text-xs mb-3">
      <div><span className="text-gray-400">Industry</span><p className="font-medium">{customer.industry || '—'}</p></div>
      <div><span className="text-gray-400">ARR</span><p className="font-medium">{formatCurrency(customer.annual_revenue)}</p></div>
      <div><span className="text-gray-400">Health</span><p className="font-medium">{customer.health_score}%</p></div>
      <div><span className="text-gray-400">Rep</span><p className="font-medium">{customer.assigned_sales_rep || 'Unassigned'}</p></div>
    </div>
    <div className="flex items-center justify-between pt-2 border-t border-gray-100 dark:border-gray-800">
      <Link to={`/customers/${customer.id}`} className="text-blue-600 text-xs font-semibold flex items-center gap-1 hover:underline">
        View Details <ArrowRight className="h-3 w-3" />
      </Link>
      <div className="flex gap-2">
        {onEdit && <button onClick={onEdit} className="text-xs text-gray-500 hover:text-blue-600">Edit</button>}
        {onDelete && <button onClick={onDelete} className="text-xs text-gray-500 hover:text-red-600">Delete</button>}
      </div>
    </div>
  </div>
);
