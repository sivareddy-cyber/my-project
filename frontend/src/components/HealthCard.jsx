import React from 'react';

export function HealthCard({ status, isChecking, lastChecked, onCheck }) {
  const getStatusBadge = () => {
    switch (status) {
      case 'connected':
        return (
          <span className="status-badge connected">
            <span className="status-dot"></span>
            ✓ Backend Connected
          </span>
        );
      case 'unavailable':
        return (
          <span className="status-badge unavailable">
            <span className="status-dot"></span>
            ✕ Backend Unavailable
          </span>
        );
      case 'checking':
        return (
          <span className="status-badge checking">
            <span className="status-spinner"></span>
            Checking Status...
          </span>
        );
      default:
        return (
          <span className="status-badge idle">
            <span className="status-dot"></span>
            Not Checked
          </span>
        );
    }
  };

  return (
    <div className="health-card">
      <div className="card-header">
        <div className="card-title-group">
          <div className="card-icon">⚡</div>
          <div>
            <h3 className="card-title">Backend Connectivity</h3>
            <p className="card-subtitle">FastAPI Core Service (http://localhost:8000)</p>
          </div>
        </div>
        <div className="status-container">{getStatusBadge()}</div>
      </div>

      <div className="card-body">
        <div className="endpoint-info">
          <span className="method-tag">GET</span>
          <span className="endpoint-path">/health</span>
          <span className="expected-response">Expected: <code>{JSON.stringify({ status: "ok" })}</code></span>
        </div>

        {lastChecked && (
          <div className="timestamp-info">
            Last checked: {lastChecked.toLocaleTimeString()}
          </div>
        )}
      </div>

      <div className="card-footer">
        <button
          id="check-backend-btn"
          className="btn-primary"
          onClick={onCheck}
          disabled={isChecking}
        >
          {isChecking ? 'Checking...' : 'Check Backend'}
        </button>
      </div>
    </div>
  );
}
