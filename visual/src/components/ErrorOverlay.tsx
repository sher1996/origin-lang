import React from 'react';

interface ErrorOverlayProps {
  error: string;
  onClose: () => void;
}

const ErrorOverlay: React.FC<ErrorOverlayProps> = ({ error, onClose }) => {
  return (
    <div className="fixed inset-0 bg-red-900 bg-opacity-90 flex items-center justify-center z-50">
      <div className="bg-red-800 p-6 rounded-lg max-w-md mx-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-red-200 font-medium text-lg">Error</h3>
          <button
            onClick={onClose}
            className="text-red-300 hover:text-red-100 transition-colors"
          >
            ✕
          </button>
        </div>
        <p className="text-red-100 text-sm mb-4">{error}</p>
        <button
          onClick={onClose}
          className="bg-red-700 hover:bg-red-600 text-red-100 px-4 py-2 rounded transition-colors"
        >
          Dismiss
        </button>
      </div>
    </div>
  );
};

export default ErrorOverlay; 