import React from 'react';

export function DemoGuideBar({
  onStepClick,
  currentStep,
}) {
  const steps = [
    {
      num: 1,
      title: '1. Load Demo Code',
      desc: 'Load payment code sample',
    },
    {
      num: 2,
      title: '2. Teach Rule',
      desc: 'Disallow console.log()',
    },
    {
      num: 3,
      title: '3. Load New Code',
      desc: 'Load checkout function',
    },
    {
      num: 4,
      title: '4. Review & Verify',
      desc: 'See Hindsight memory in action',
    },
  ];

  return (
    <div className="demo-guide-container">
      <div className="guide-header">
        <span className="guide-tag">⚡ 60-Second Demo Walkthrough</span>
        <span className="guide-hint">Click any step to auto-load demo states:</span>
      </div>

      <div className="steps-row">
        {steps.map((s) => (
          <button
            key={s.num}
            type="button"
            className={`step-btn ${currentStep === s.num ? 'active' : ''}`}
            onClick={() => onStepClick(s.num)}
          >
            <span className="step-badge">{s.num}</span>
            <div className="step-info">
              <span className="step-title">{s.title}</span>
              <span className="step-desc">{s.desc}</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
