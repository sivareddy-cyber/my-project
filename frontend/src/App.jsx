import React, { useState, useEffect } from 'react';
import { checkBackendHealth, teachMemory, reviewCode } from './services/api';
import { CodeReviewSection } from './components/CodeReviewSection';
import { TeachAgentCard } from './components/TeachAgentCard';
import { ReviewResultSection } from './components/ReviewResultSection';
import { DemoGuideBar } from './components/DemoGuideBar';
import './App.css';

const DEMO_CODE_1 = `function processPayment(paymentDetails) {
  console.log("Processing payment for user:", paymentDetails.userId);
  const success = chargeCard(paymentDetails.amount);
  return { success, timestamp: Date.now() };
}`;

const DEMO_CODE_2 = `function checkout(order) {
  console.log("Processing order:", order);
  processPayment(order);
}`;

const DEFAULT_RULE = "Our team does not allow console.log() in production code. Use the structured logger instead.";

function App() {
  // Application State
  const [code, setCode] = useState(DEMO_CODE_1);
  const [language, setLanguage] = useState('javascript');
  const [ruleContent, setRuleContent] = useState(DEFAULT_RULE);
  
  // Status & Async States
  const [backendActive, setBackendActive] = useState(false);
  const [isReviewing, setIsReviewing] = useState(false);
  const [reviewResult, setReviewResult] = useState(null);
  const [reviewError, setReviewError] = useState(null);

  const [isTeaching, setIsTeaching] = useState(false);
  const [teachSuccess, setTeachSuccess] = useState(false);
  const [teachError, setTeachError] = useState(null);

  const [currentStep, setCurrentStep] = useState(1);

  // Initial Backend Health Ping
  useEffect(() => {
    checkBackendHealth()
      .then((res) => {
        if (res && res.status === 'ok') setBackendActive(true);
      })
      .catch((err) => {
        console.warn('Backend currently unreachable:', err);
        setBackendActive(false);
      });
  }, []);

  // Handle Code Review
  const handleReviewCode = async () => {
    if (!code.trim()) {
      setReviewError('Please provide source code to review.');
      return;
    }

    setIsReviewing(true);
    setReviewError(null);
    try {
      const result = await reviewCode(code, language);
      setReviewResult(result);
    } catch (err) {
      console.error('Review failed:', err);
      setReviewError(err.message || 'Failed to complete code review with AI.');
    } finally {
      setIsReviewing(false);
    }
  };

  // Handle Teaching Agent / Retaining Rule in Hindsight
  const handleTeachAgent = async () => {
    if (!ruleContent.trim()) {
      setTeachError('Please enter a team rule or standard.');
      return;
    }

    setIsTeaching(true);
    setTeachError(null);
    setTeachSuccess(false);

    try {
      const result = await teachMemory(ruleContent);
      if (result && result.status === 'success') {
        setTeachSuccess(true);
      } else {
        throw new Error('Hindsight memory retention did not return success.');
      }
    } catch (err) {
      console.error('Teach failed:', err);
      setTeachError(err.message || 'Failed to retain rule in Hindsight memory.');
    } finally {
      setIsTeaching(false);
    }
  };

  // Handle Load Demo Samples
  const handleLoadDemo = (sampleNumber) => {
    if (sampleNumber === 1) {
      setCode(DEMO_CODE_1);
      setCurrentStep(1);
    } else if (sampleNumber === 2) {
      setCode(DEMO_CODE_2);
      setCurrentStep(3);
    }
    setReviewError(null);
  };

  // Handle Demo Step Click
  const handleStepClick = (stepNum) => {
    setCurrentStep(stepNum);
    if (stepNum === 1) {
      setCode(DEMO_CODE_1);
      setReviewError(null);
    } else if (stepNum === 2) {
      setRuleContent(DEFAULT_RULE);
      setTeachSuccess(false);
    } else if (stepNum === 3) {
      setCode(DEMO_CODE_2);
      setReviewError(null);
    } else if (stepNum === 4) {
      handleReviewCode();
    }
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="header-brand">
          <div className="brand-logo">🧠</div>
          <div className="brand-text">
            <h1 className="brand-title">CodeReview Memory Agent</h1>
            <p className="brand-subtitle">AI code review that learns your team's standards.</p>
          </div>
        </div>

        <div className="header-status-pill">
          <span className={`status-dot ${backendActive ? 'active' : 'offline'}`}></span>
          <span className="status-text">
            {backendActive ? 'Hindsight Memory Active' : 'Connecting to Backend...'}
          </span>
        </div>
      </header>

      {/* Main Container */}
      <main className="main-content">
        {/* Interactive Demo Guide Bar */}
        <DemoGuideBar
          currentStep={currentStep}
          onStepClick={handleStepClick}
        />

        {/* 2-Column Split View */}
        <div className="app-grid">
          {/* Left Column: Code Review Input + Teach Card */}
          <div className="grid-column left-column">
            <CodeReviewSection
              code={code}
              setCode={setCode}
              language={language}
              setLanguage={setLanguage}
              onReview={handleReviewCode}
              isLoading={isReviewing}
              onLoadDemo={handleLoadDemo}
              error={reviewError}
            />

            <TeachAgentCard
              ruleContent={ruleContent}
              setRuleContent={setRuleContent}
              onTeach={handleTeachAgent}
              isTeaching={isTeaching}
              teachSuccess={teachSuccess}
              teachError={teachError}
              onResetStatus={() => {
                setTeachSuccess(false);
                setTeachError(null);
              }}
            />
          </div>

          {/* Right Column: Review Results & Memories Used */}
          <div className="grid-column right-column">
            <ReviewResultSection
              reviewResult={reviewResult}
              isReviewing={isReviewing}
            />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <span>CodeReview Memory Agent &bull; Powered by Real Hindsight Agent Memory + Groq LLM</span>
      </footer>
    </div>
  );
}

export default App;
