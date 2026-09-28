import React from 'react';

export function CodeReviewSection({
  code,
  setCode,
  language,
  setLanguage,
  onReview,
  isLoading,
  onLoadDemo,
  error,
}) {
  return (
    <div className="section-card code-input-card">
      <div className="card-top-bar">
        <div className="section-heading">
          <span className="section-icon">💻</span>
          <div>
            <h3>Submit Code for Review</h3>
            <p className="section-subtitle">AI analyzes code against general best practices & team memory</p>
          </div>
        </div>

        <div className="editor-controls">
          <select
            className="lang-select"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            disabled={isLoading}
          >
            <option value="javascript">JavaScript</option>
            <option value="typescript">TypeScript</option>
            <option value="python">Python</option>
          </select>
        </div>
      </div>

      <div className="demo-code-presets">
        <span className="preset-label">Demo Presets:</span>
        <button
          type="button"
          className="btn-preset"
          onClick={() => onLoadDemo(1)}
          disabled={isLoading}
        >
          Sample 1: Payment Function
        </button>
        <button
          type="button"
          className="btn-preset"
          onClick={() => onLoadDemo(2)}
          disabled={isLoading}
        >
          Sample 2: Checkout Function
        </button>
      </div>

      <div className="editor-wrapper">
        <textarea
          id="code-input-area"
          className="code-textarea"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder="Paste or write code here to review..."
          rows={10}
          spellCheck={false}
          disabled={isLoading}
        />
      </div>

      {error && (
        <div className="error-banner">
          <span className="error-icon">✕</span>
          <span>{error}</span>
        </div>
      )}

      <div className="card-action-row">
        <button
          id="review-code-btn"
          className="btn-primary btn-review"
          onClick={onReview}
          disabled={isLoading || !code.trim()}
        >
          {isLoading ? (
            <>
              <span className="status-spinner"></span>
              Recalling Hindsight Memory & Reviewing...
            </>
          ) : (
            '⚡ Review Code'
          )}
        </button>
      </div>
    </div>
  );
}
