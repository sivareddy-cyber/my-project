import React from 'react';

export function ReviewResultSection({ reviewResult, isReviewing }) {
  if (isReviewing) {
    return (
      <div className="section-card review-result-card loading-container">
        <div className="loader-box">
          <div className="pulse-circle">🧠</div>
          <h4>Analyzing Code with Hindsight Memory</h4>
          <p>Recalling team rules from Hindsight & running Groq code review...</p>
        </div>
      </div>
    );
  }

  if (!reviewResult) {
    return (
      <div className="section-card review-result-card placeholder-container">
        <div className="empty-state">
          <div className="empty-icon">📋</div>
          <h4>No Review Generated Yet</h4>
          <p>Click "Review Code" above to trigger a team-aware AI code review.</p>
        </div>
      </div>
    );
  }

  const { summary, issues = [], memories_used = [] } = reviewResult;

  // Helper to determine if an issue was influenced by team memory
  const isTeamSpecificIssue = (issue) => {
    const text = `${issue.description} ${issue.suggestion || ''}`.toLowerCase();
    const hasMemoryInfluence = memories_used.some((mem) => {
      const keywords = mem.toLowerCase().split(' ').filter(w => w.length > 4);
      return keywords.some(k => text.includes(k));
    });
    return hasMemoryInfluence || text.includes('team') || text.includes('console.log') || text.includes('convention') || text.includes('standard');
  };

  return (
    <div className="section-card review-result-card">
      <div className="card-top-bar">
        <div className="section-heading">
          <span className="section-icon">📊</span>
          <div>
            <h3>Code Review Findings</h3>
            <p className="section-subtitle">Evaluated with Groq LLM & active team knowledge</p>
          </div>
        </div>
      </div>

      {/* Summary Box */}
      <div className="review-summary-box">
        <strong className="summary-title">Review Summary:</strong>
        <p className="summary-text">{summary}</p>
      </div>

      {/* Memories Used - Prominent Showcase */}
      <div className="memories-showcase-box">
        <div className="memories-header">
          <div className="memories-title">
            <span className="memory-badge-icon">🧠</span>
            <strong>Memories Used</strong>
          </div>
          <span className="hindsight-source-tag">Recalled from Hindsight</span>
        </div>

        {memories_used && memories_used.length > 0 ? (
          <ul className="memories-list">
            {memories_used.map((mem, idx) => (
              <li key={idx} className="memory-item">
                <span className="memory-quote">“{mem}”</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="no-memories-text">
            No team memories applied for this review. (Teach the agent a rule to see team-aware memory in action!)
          </p>
        )}
      </div>

      {/* Issues List */}
      <div className="issues-container">
        <h4 className="issues-heading">
          Detected Issues ({issues.length})
        </h4>

        {issues.length === 0 ? (
          <div className="no-issues-box">
            <span>✓ No issues or violations detected. Clean code!</span>
          </div>
        ) : (
          <div className="issues-list">
            {issues.map((issue, idx) => {
              const teamSpecific = isTeamSpecificIssue(issue);
              return (
                <div
                  key={idx}
                  className={`issue-card ${issue.severity || 'warning'} ${teamSpecific ? 'team-specific-card' : ''}`}
                >
                  <div className="issue-header">
                    <div className="issue-badges">
                      {teamSpecific && (
                        <span className="badge-team-specific">
                          🔴 TEAM-SPECIFIC ISSUE
                        </span>
                      )}
                      <span className={`badge-severity ${(issue.severity || 'warning').toLowerCase()}`}>
                        {(issue.severity || 'WARNING').toUpperCase()}
                      </span>
                      {issue.line && (
                        <span className="badge-line">
                          Line {issue.line}
                        </span>
                      )}
                    </div>
                  </div>

                  <p className="issue-description">{issue.description}</p>

                  {issue.suggestion && (
                    <div className="issue-suggestion-box">
                      <span className="suggestion-label">Suggestion:</span>
                      <p className="suggestion-text">{issue.suggestion}</p>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
