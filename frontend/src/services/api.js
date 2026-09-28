const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Checks the operational health of the backend FastAPI service.
 */
export async function checkBackendHealth() {
  const response = await fetch(`${API_BASE_URL}/health`, {
    method: 'GET',
    headers: { 'Accept': 'application/json' },
  });

  if (!response.ok) {
    throw new Error(`Health check failed with status: ${response.status}`);
  }
  return response.json();
}

/**
 * Teaches/retains a new team rule into real Hindsight memory.
 * @param {string} content - The rule or coding preference to teach.
 */
export async function teachMemory(content) {
  const response = await fetch(`${API_BASE_URL}/memory`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify({ content }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Network error' }));
    throw new Error(errorData.detail || `Memory retain failed with status ${response.status}`);
  }
  return response.json();
}

/**
 * Submits code to be reviewed by Groq LLM with Hindsight recalled memory.
 * @param {string} code - The source code to review.
 * @param {string} language - Programming language (e.g. 'javascript').
 */
export async function reviewCode(code, language = 'javascript') {
  const response = await fetch(`${API_BASE_URL}/review`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify({ code, language }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Network error' }));
    throw new Error(errorData.detail || `Code review failed with status ${response.status}`);
  }
  return response.json();
}

/**
 * Submits developer feedback to be distilled and retained in Hindsight.
 * @param {object} feedbackData
 */
export async function submitFeedback(feedbackData) {
  const response = await fetch(`${API_BASE_URL}/feedback`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(feedbackData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Network error' }));
    throw new Error(errorData.detail || `Feedback submission failed with status ${response.status}`);
  }
  return response.json();
}
