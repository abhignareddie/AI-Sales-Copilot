import { useForm } from 'react-hook-form';
import type { CustomerFormData } from '../../types';

interface CustomerFormProps {
  defaultValues?: Partial<CustomerFormData>;
  onSubmit: (data: CustomerFormData) => void;
  onCancel: () => void;
  loading?: boolean;
}

const inputClass = 'w-full p-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-800 rounded-lg text-sm focus:ring-1 focus:ring-blue-500 focus:outline-none';
const labelClass = 'text-xs font-bold text-gray-500 uppercase block mb-1';

export const CustomerForm = ({ defaultValues, onSubmit, onCancel, loading }: CustomerFormProps) => {
  const { register, handleSubmit, formState: { errors } } = useForm<CustomerFormData>({
    defaultValues: {
      current_stage: 'prospect',
      ...defaultValues,
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className={labelClass}>Company Name *</label>
          <input {...register('company_name', { required: 'Company name is required' })} className={inputClass} />
          {errors.company_name && <p className="text-xs text-red-500 mt-1">{errors.company_name.message}</p>}
        </div>
        <div>
          <label className={labelClass}>Customer Name *</label>
          <input {...register('contact_person', { required: 'Customer name is required' })} className={inputClass} />
          {errors.contact_person && <p className="text-xs text-red-500 mt-1">{errors.contact_person.message}</p>}
        </div>
        <div>
          <label className={labelClass}>Email *</label>
          <input {...register('email', { required: 'Email is required', pattern: { value: /^\S+@\S+\.\S+$/, message: 'Valid email required' } })} type="email" className={inputClass} />
          {errors.email && <p className="text-xs text-red-500 mt-1">{errors.email.message}</p>}
        </div>
        <div>
          <label className={labelClass}>Phone</label>
          <input {...register('phone')} className={inputClass} />
        </div>
        <div>
          <label className={labelClass}>Industry</label>
          <input {...register('industry')} className={inputClass} />
        </div>
        <div>
          <label className={labelClass}>Annual Revenue</label>
          <input {...register('annual_revenue')} type="number" className={inputClass} />
        </div>
        <div>
          <label className={labelClass}>Deal Stage *</label>
          <select {...register('current_stage', { required: 'Deal stage is required' })} className={inputClass}>
            {['prospect', 'qualified', 'proposal', 'negotiation', 'closed_won', 'closed_lost'].map(s => (
              <option key={s} value={s}>{s.replace('_', ' ')}</option>
            ))}
          </select>
        </div>
        <div>
          <label className={labelClass}>Country</label>
          <input {...register('country')} className={inputClass} />
        </div>
        <div>
          <label className={labelClass}>Assigned Sales Rep</label>
          <input {...register('assigned_sales_rep')} className={inputClass} />
        </div>
      </div>
      <div>
        <label className={labelClass}>Notes</label>
        <textarea {...register('notes')} rows={3} className={inputClass} />
      </div>
      <div className="flex justify-end gap-2 pt-2">
        <button type="button" onClick={onCancel} className="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg">Cancel</button>
        <button type="submit" disabled={loading} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-lg disabled:opacity-50">
          {loading ? 'Saving...' : 'Save Customer'}
        </button>
      </div>
    </form>
  );
};
