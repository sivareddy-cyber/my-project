import React from 'react';

export function TeachAgentCard({
  ruleContent,
  setRuleContent,
  onTeach,
  isTeaching,
  teachSuccess,
  teachError,
  onResetStatus,
}) {
  return (
    <div className="section-card teach-agent-card">
      <div className="card-top-bar">
        <div className="section-heading">
          <span className="section-icon memory-icon">🧠</span>
          <div>
            <h3>Teach Your Agent</h3>
            <p className="section-subtitle">
              Give your team a coding rule or preference. The agent will remember it for future reviews.
            </p>
          </div>
        </div>
      </div>

      <div className="teach-body">
        <textarea
          id="teach-rule-input"
          className="teach-textarea"
          value={ruleContent}
          onChange={(e) => {
            setRuleContent(e.target.value);
            if (teachSuccess || teachError) onResetStatus();
          }}
          placeholder="e.g. Our team does not allow console.log() in production code. Use the structured logger instead."
          rows={3}
          disabled={isTeaching}
        />

        {teachSuccess && (
          <div className="success-banner">
            <div className="success-header">
              <span className="success-badge-icon">✓</span>
              <strong>Agent learned this team rule</strong>
            </div>
            <p className="success-detail">
              Stored persistently in Hindsight Memory Bank. Future code reviews will enforce this standard.
            </p>
          </div>
        )}

        {teachError && (
          <div className="error-banner">
            <span className="error-icon">✕</span>
            <span>{teachError}</span>
          </div>
        )}

        <div className="teach-action-row">
          <button
            id="teach-agent-btn"
            className="btn-teach"
            onClick={onTeach}
            disabled={isTeaching || !ruleContent.trim()}
          >
            {isTeaching ? (
              <>
                <span className="status-spinner"></span>
                Retaining in Hindsight...
              </>
            ) : (
              '🧠 Teach Agent'
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
