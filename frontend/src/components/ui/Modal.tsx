import { X } from 'lucide-react';

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

const sizeMap = { sm: 'max-w-md', md: 'max-w-lg', lg: 'max-w-2xl', xl: 'max-w-4xl' };

export const Modal = ({ open, onClose, title, children, size = 'md' }: ModalProps) => {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />
      <div className={`relative w-full ${sizeMap[size]} bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl shadow-2xl max-h-[90vh] overflow-y-auto`}>
        <div className="flex items-center justify-between p-5 border-b border-gray-200 dark:border-gray-800 sticky top-0 bg-white dark:bg-gray-900 z-10">
          <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100">{title}</h2>
          <button onClick={onClose} className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
            <X className="h-5 w-5" />
          </button>
        </div>
        <div className="p-5">{children}</div>
      </div>
    </div>
  );
};

interface ConfirmDialogProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmLabel?: string;
  destructive?: boolean;
}

export const ConfirmDialog = ({ open, onClose, onConfirm, title, message, confirmLabel = 'Confirm', destructive }: ConfirmDialogProps) => (
  <Modal open={open} onClose={onClose} title={title} size="sm">
    <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">{message}</p>
    <div className="flex justify-end space-x-2">
      <button onClick={onClose} className="px-4 py-2 text-sm font-medium text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg">
        Cancel
      </button>
      <button
        onClick={() => { onConfirm(); onClose(); }}
        className={`px-4 py-2 text-sm font-semibold text-white rounded-lg ${destructive ? 'bg-red-600 hover:bg-red-700' : 'bg-blue-600 hover:bg-blue-700'}`}
      >
        {confirmLabel}
      </button>
    </div>
  </Modal>
);
