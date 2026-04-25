import { FC } from 'react';
import { useToast, Toast as ToastType } from '../context/ToastContext';
import './ToastContainer.css';

const ToastItem: FC<{ toast: ToastType }> = ({ toast }) => {
  const { hideToast } = useToast();

  const icons: Record<string, string> = {
    success: '\u2713',
    error: '\u2717',
    warning: '\u26A0',
    info: '\u2139',
  };

  return (
    <div className={`toast toast-${toast.type}`}>
      <span className="toast-icon">{icons[toast.type]}</span>
      <span className="toast-message">{toast.message}</span>
      <button className="toast-close" onClick={() => hideToast(toast.id)}>
        &times;
      </button>
    </div>
  );
};

const ToastContainer: FC = () => {
  const { toasts } = useToast();

  if (toasts.length === 0) return null;

  return (
    <div className="toast-container">
      {toasts.map(toast => (
        <ToastItem key={toast.id} toast={toast} />
      ))}
    </div>
  );
};

export default ToastContainer;