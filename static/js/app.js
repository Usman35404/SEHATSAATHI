/**
 * SehatSaathi AI — Frontend Controller (Vanilla JS)
 *
 * Security & Healthcare Integrity Rules:
 * - Never embeds API keys or credentials.
 * - Sends only allowlisted { topic_id, language } to /api/explain.
 * - Renders all model output strictly via textContent (never innerHTML) to prevent XSS.
 * - Never substitutes canned text as fake AI output on failure.
 * - Applies lang="ur" and dir="rtl" dynamically to Urdu educational blocks.
 */

(() => {
  "use strict";

  const state = {
    selectedTopicId: "handwashing",
    selectedLanguage: "en",
    isLoading: false,
    activeRequestId: 0,
    currentResult: null,
    activeFollowupRequestId: 0,
  };

  // DOM References
  const topicButtons = Array.from(document.querySelectorAll(".topic-card"));
  const langEnBtn = document.getElementById("lang-en-btn");
  const langUrBtn = document.getElementById("lang-ur-btn");
  const fontSizeBtn = document.getElementById("font-size-btn");

  const selectedTopicLabel = document.getElementById("selected-topic-label");
  const selectedLangLabel = document.getElementById("selected-lang-label");
  const explainBtn = document.getElementById("explain-btn");
  const explainBtnText = document.getElementById("explain-btn-text");

  const emptyState = document.getElementById("empty-state");
  const loadingState = document.getElementById("loading-state");
  const errorState = document.getElementById("error-state");
  const errorTitle = document.getElementById("error-title");
  const errorMessage = document.getElementById("error-message");
  const retryBtn = document.getElementById("retry-btn");
  const resultContainer = document.getElementById("result-container");

  const resultLangBadge = document.getElementById("result-lang-badge");
  const localizedExplanationRegion = document.getElementById("localized-explanation-region");
  const resultTopicHeading = document.getElementById("result-topic-heading");
  const resultExplanation = document.getElementById("result-explanation");
  const keyPointsHeading = document.getElementById("key-points-heading");
  const resultKeyPoints = document.getElementById("result-key-points");
  const sourceTitleText = document.getElementById("source-title-text");
  const sourceUrlLink = document.getElementById("source-url-link");

  // Speech Synthesis Controls
  const listenBtn = document.getElementById("listen-btn");
  const listenBtnLabel = document.getElementById("listen-btn-label");
  const stopAudioBtn = document.getElementById("stop-audio-btn");
  const speechStatusNote = document.getElementById("speech-status-note");

  // Quiz Elements
  const localizedQuizRegion = document.getElementById("localized-quiz-region");
  const quizQuestionText = document.getElementById("quiz-question-text");
  const quizForm = document.getElementById("quiz-form");
  const quizOptionsList = document.getElementById("quiz-options-list");
  const submitQuizBtn = document.getElementById("submit-quiz-btn");
  const quizFeedbackBox = document.getElementById("quiz-feedback-box");
  const quizFeedbackStatus = document.getElementById("quiz-feedback-status");
  const quizFeedbackText = document.getElementById("quiz-feedback-text");

  // Follow-up Elements
  const followupForm = document.getElementById("followup-form");
  const followupInput = document.getElementById("followup-input");
  const followupSubmitBtn = document.getElementById("followup-submit-btn");
  const followupLoading = document.getElementById("followup-loading");
  const followupError = document.getElementById("followup-error");
  const followupResult = document.getElementById("followup-result");
  const followupBadge = document.getElementById("followup-badge");
  const followupSourceNote = document.getElementById("followup-source-note");
  const followupAnswerText = document.getElementById("followup-answer-text");
  const directAskTopicName = document.getElementById("direct-ask-topic-name");

  // Usability helpers (loading progress, model badge, suggestions, config check)
  const loadingElapsed = document.getElementById("loading-elapsed");
  const loadingStepText = document.getElementById("loading-step-text");
  const resultMetaBadge = document.getElementById("result-meta-badge");
  const followupSuggestions = document.getElementById("followup-suggestions");
  const configWarning = document.getElementById("config-warning");
  let loadingTimer = null;
  let requestStartedAt = 0;

  const LOADING_STEPS = [
    "Reading approved CDC facts…",
    "Asking Gemini for a plain-language explanation…",
    "Creating your comprehension question…",
    "Checking the response format…",
    "Gemini is busy — still waiting for a live answer…",
  ];

  const SUGGESTED_QUESTIONS = {
    handwashing: {
      en: ["How long should I scrub my hands?", "When should I wash my hands?", "Can I use hand sanitizer instead?"],
      ur: ["ہاتھ کتنی دیر تک دھونے چاہئیں؟", "ہاتھ کب کب دھونے چاہئیں؟", "کیا سینیٹائزر استعمال کر سکتے ہیں؟"],
    },
    sleep: {
      en: ["How many hours should a teenager sleep?", "How can I sleep better at night?", "Why is sleep important?"],
      ur: ["نوجوانوں کو کتنے گھنٹے سونا چاہیے؟", "رات کو بہتر نیند کیسے لیں؟", "نیند کیوں ضروری ہے؟"],
    },
    activity: {
      en: ["What are the immediate benefits of physical activity?", "How does exercise help bones and muscles?", "How does activity help children?"],
      ur: ["جسمانی سرگرمی کے فوری فوائد کیا ہیں؟", "ورزش ہڈیوں اور پٹھوں کو کیسے مضبوط کرتی ہے؟", "بچوں کے لیے ورزش کیوں ضروری ہے؟"],
    },
    hydration: {
      en: ["Why is drinking enough water important?", "What are healthy alternatives to sugary drinks?", "How can I drink more water daily?"],
      ur: ["مناسب مقدار میں پانی پینا کیوں ضروری ہے؟", "میٹھے مشروبات کا صحت مند متبادل کیا ہے؟", "روزانہ زیادہ پانی پینے کے آسان طریقے کیا ہیں؟"],
    },
  };

  function startLoadingTimer() {
    requestStartedAt = Date.now();
    if (loadingElapsed) loadingElapsed.textContent = "0s";
    if (loadingStepText) loadingStepText.textContent = LOADING_STEPS[0];
    clearInterval(loadingTimer);
    loadingTimer = setInterval(() => {
      const secs = Math.floor((Date.now() - requestStartedAt) / 1000);
      if (loadingElapsed) loadingElapsed.textContent = `${secs}s`;
      const stepIdx = secs < 2 ? 0 : secs < 5 ? 1 : secs < 8 ? 2 : secs < 12 ? 3 : 4;
      if (loadingStepText) loadingStepText.textContent = LOADING_STEPS[stepIdx];
    }, 500);
  }

  function stopLoadingTimer() {
    clearInterval(loadingTimer);
    loadingTimer = null;
  }

  function renderSuggestions(topicId, langCode) {
    if (!followupSuggestions) return;
    followupSuggestions.textContent = "";
    const list = (SUGGESTED_QUESTIONS[topicId] || {})[langCode] || [];
    followupSuggestions.setAttribute("dir", langCode === "ur" ? "rtl" : "ltr");
    list.forEach((q) => {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "suggestion-chip";
      chip.textContent = q;
      if (langCode === "ur") chip.setAttribute("lang", "ur");
      chip.addEventListener("click", () => {
        followupInput.value = q;
        if (typeof followupForm.requestSubmit === "function") {
          followupForm.requestSubmit();
        } else {
          followupForm.dispatchEvent(new Event("submit", { cancelable: true }));
        }
      });
      followupSuggestions.appendChild(chip);
    });
  }

  async function checkAiConfiguration() {
    if (!configWarning) return;
    try {
      const resp = await fetch("/api/health");
      const data = await resp.json();
      configWarning.classList.toggle("hidden", data && data.ai_configured === true);
    } catch {
      /* Server unreachable: the explain request will show its own error. */
    }
  }

  function stopSpeech() {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
    if (stopAudioBtn) {
      stopAudioBtn.classList.add("hidden");
    }
    if (listenBtnLabel) {
      listenBtnLabel.textContent = "Listen";
    }
  }

  function getMatchingVoice(langCode) {
    if (!("speechSynthesis" in window)) {
      return null;
    }
    const voices = window.speechSynthesis.getVoices() || [];
    const targetPrefix = langCode === "ur" ? "ur" : "en";
    return (
      voices.find((v) => v.lang && v.lang.toLowerCase().startsWith(targetPrefix)) ||
      null
    );
  }

  function updateSpeechAvailability(langCode) {
    stopSpeech();
    if (!("speechSynthesis" in window)) {
      listenBtn.disabled = true;
      speechStatusNote.textContent = "Voice read-aloud is not supported in this browser.";
      speechStatusNote.classList.remove("hidden");
      return;
    }

    const matchingVoice = getMatchingVoice(langCode);
    if (!matchingVoice) {
      listenBtn.disabled = true;
      speechStatusNote.textContent = `${langCode === "ur" ? "Urdu" : "English"} voice is not installed on this device.`;
      speechStatusNote.classList.remove("hidden");
    } else {
      listenBtn.disabled = false;
      speechStatusNote.textContent = "";
      speechStatusNote.classList.add("hidden");
    }
  }

  function clearStaleResults() {
    ++state.activeRequestId;
    setLoadingState(false);
    stopSpeech();
    state.currentResult = null;
    resultContainer.classList.add("hidden");
    errorState.classList.add("hidden");
    loadingState.classList.add("hidden");
    emptyState.classList.remove("hidden");
    resetFollowupUI();
  }

  function updateSelectionUI() {
    const activeCard = topicButtons.find(
      (btn) => btn.dataset.topicId === state.selectedTopicId
    );
    topicButtons.forEach((btn) => {
      const isSelected = btn.dataset.topicId === state.selectedTopicId;
      btn.classList.toggle("is-selected", isSelected);
      btn.setAttribute("aria-checked", isSelected ? "true" : "false");
    });

    if (activeCard && selectedTopicLabel) {
      const labelText =
        state.selectedLanguage === "ur"
          ? `${activeCard.dataset.titleEn} (${activeCard.dataset.titleUr})`
          : activeCard.dataset.titleEn;
      selectedTopicLabel.textContent = labelText;
      if (directAskTopicName) {
        directAskTopicName.textContent = labelText;
      }
    }

    renderSuggestions(state.selectedTopicId, state.selectedLanguage);

    const isUrdu = state.selectedLanguage === "ur";
    langEnBtn.classList.toggle("is-active", !isUrdu);
    langEnBtn.setAttribute("aria-checked", !isUrdu ? "true" : "false");
    langUrBtn.classList.toggle("is-active", isUrdu);
    langUrBtn.setAttribute("aria-checked", isUrdu ? "true" : "false");

    if (selectedLangLabel) {
      selectedLangLabel.textContent = isUrdu ? "اردو (Urdu)" : "English";
    }

    if (followupInput) {
      followupInput.dir = isUrdu ? "rtl" : "ltr";
      followupInput.placeholder = isUrdu
        ? "اس موضوع کے بارے میں مختصر تعلیمی سوال پوچھیں..."
        : "e.g., How many seconds should I scrub my hands with soap?";
    }
  }

  function setLoadingState(loading) {
    state.isLoading = loading;
    explainBtn.disabled = loading;
    explainBtnText.textContent = loading ? "Generating with Live AI..." : "Explain with AI";

    if (loading) {
      stopSpeech();
      startLoadingTimer();
      emptyState.classList.add("hidden");
      errorState.classList.add("hidden");
      resultContainer.classList.add("hidden");
      loadingState.classList.remove("hidden");
    } else {
      stopLoadingTimer();
      loadingState.classList.add("hidden");
    }
  }

  function showErrorState(title, message) {
    stopSpeech();
    emptyState.classList.add("hidden");
    loadingState.classList.add("hidden");
    resultContainer.classList.add("hidden");
    errorTitle.textContent = title || "Live AI couldn't respond right now";
    errorMessage.textContent =
      message ||
      "Live AI is temporarily unavailable. Please verify your connection or configuration and try again.";
    errorState.classList.remove("hidden");
  }

  function renderQuiz(quizData, langCode) {
    const isUrdu = langCode === "ur";
    localizedQuizRegion.setAttribute("lang", isUrdu ? "ur" : "en");
    localizedQuizRegion.setAttribute("dir", isUrdu ? "rtl" : "ltr");

    quizQuestionText.textContent = quizData.question;
    quizOptionsList.textContent = "";
    quizFeedbackBox.classList.add("hidden");
    quizFeedbackBox.classList.remove("is-correct", "is-incorrect");
    submitQuizBtn.disabled = true;

    quizData.options.forEach((optionText, idx) => {
      const label = document.createElement("label");
      label.className = "quiz-option-label";

      const radio = document.createElement("input");
      radio.type = "radio";
      radio.name = "quiz-option";
      radio.value = String(idx);
      radio.addEventListener("change", () => {
        submitQuizBtn.disabled = false;
      });

      const span = document.createElement("span");
      span.textContent = optionText;

      label.appendChild(radio);
      label.appendChild(span);
      quizOptionsList.appendChild(label);
    });
  }

  function resetFollowupUI() {
    ++state.activeFollowupRequestId;
    followupSubmitBtn.disabled = false;
    if (followupInput) {
      followupInput.value = "";
    }
    if (followupLoading) {
      followupLoading.classList.add("hidden");
    }
    if (followupError) {
      followupError.classList.add("hidden");
      followupError.textContent = "";
    }
    if (followupResult) {
      followupResult.classList.add("hidden");
    }
    if (followupAnswerText) {
      followupAnswerText.textContent = "";
    }
  }

  function renderExplanationResult(data) {
    if (!data || data.live_ai !== true) {
      showErrorState(
        "Unverified AI Response",
        "The server did not confirm a live AI response."
      );
      return;
    }

    state.currentResult = data;
    const isUrdu = data.language === "ur";

    resultLangBadge.textContent = isUrdu ? "اردو (Urdu)" : "English";

    localizedExplanationRegion.setAttribute("lang", isUrdu ? "ur" : "en");
    localizedExplanationRegion.setAttribute("dir", isUrdu ? "rtl" : "ltr");

    resultTopicHeading.textContent = data.topic_title || data.topic_id;
    resultExplanation.textContent = data.explanation;

    keyPointsHeading.textContent = isUrdu ? "اہم نکات (Key Takeaways)" : "Key Takeaways";
    resultKeyPoints.textContent = "";
    (data.key_points || []).forEach((pt) => {
      const li = document.createElement("li");
      li.textContent = pt;
      resultKeyPoints.appendChild(li);
    });

    // Source Attribution (always server-verified)
    const srcTitle = data.source && data.source.title ? data.source.title : "CDC Public Health";
    const srcUrl = data.source && data.source.url ? data.source.url : "https://www.cdc.gov/";
    sourceTitleText.textContent = srcTitle;
    sourceUrlLink.textContent = srcUrl;
    sourceUrlLink.href = srcUrl;

    renderQuiz(data.quiz, data.language);
    resetFollowupUI();
    renderSuggestions(data.topic_id, data.language);
    updateSpeechAvailability(data.language);

    if (resultMetaBadge) {
      const secs = requestStartedAt ? ((Date.now() - requestStartedAt) / 1000).toFixed(1) : null;
      const parts = [];
      if (data.model) parts.push(String(data.model).replace(/^models\//, ""));
      if (secs) parts.push(`${secs}s`);
      resultMetaBadge.textContent = parts.join(" · ");
      resultMetaBadge.classList.toggle("hidden", parts.length === 0);
    }

    emptyState.classList.add("hidden");
    errorState.classList.add("hidden");
    loadingState.classList.add("hidden");
    resultContainer.classList.remove("hidden");
    if (window.matchMedia && window.matchMedia("(max-width: 900px)").matches) {
      resultContainer.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  async function requestExplanation() {
    if (state.isLoading) {
      return;
    }

    const requestId = ++state.activeRequestId;
    setLoadingState(true);

    try {
      const response = await fetch("/api/explain", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic_id: state.selectedTopicId,
          language: state.selectedLanguage,
        }),
      });

      if (requestId !== state.activeRequestId) {
        return; // Stale response ignored
      }

      let payload = null;
      try {
        payload = await response.json();
      } catch {
        payload = null;
      }

      if (requestId !== state.activeRequestId) {
        return;
      }
      setLoadingState(false);

      if (!response.ok || !payload || payload.error) {
        const errMsg =
          payload && payload.error && payload.error.message
            ? payload.error.message
            : "Live AI couldn't respond right now. Please try again.";
        showErrorState("Live AI couldn't respond right now", errMsg);
        return;
      }

      renderExplanationResult(payload);
    } catch {
      if (requestId !== state.activeRequestId) {
        return;
      }
      setLoadingState(false);
      showErrorState(
        "Network or Server Connection Issue",
        "Could not reach the local SehatSaathi server. Please check that the server is running and try again."
      );
    }
  }

  // Event Listeners: Topic Cards
  topicButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const newTopicId = btn.dataset.topicId;
      if (newTopicId && newTopicId !== state.selectedTopicId) {
        state.selectedTopicId = newTopicId;
        updateSelectionUI();
        clearStaleResults();
      }
    });
  });

  // Event Listeners: Language Switch
  [langEnBtn, langUrBtn].forEach((btn) => {
    if (!btn) return;
    btn.addEventListener("click", () => {
      const newLang = btn.dataset.lang;
      if (newLang && newLang !== state.selectedLanguage) {
        state.selectedLanguage = newLang;
        updateSelectionUI();
        clearStaleResults();
      }
    });
  });

  // Event Listener: Large Font Toggle
  if (fontSizeBtn) {
    fontSizeBtn.addEventListener("click", () => {
      const isLarge = document.documentElement.classList.toggle("large-text");
      fontSizeBtn.setAttribute("aria-pressed", isLarge ? "true" : "false");
    });
  }

  // Event Listeners: Explain & Retry
  if (explainBtn) {
    explainBtn.addEventListener("click", requestExplanation);
  }
  if (retryBtn) {
    retryBtn.addEventListener("click", requestExplanation);
  }

  // Event Listener: Quiz Submission
  if (quizForm) {
    quizForm.addEventListener("submit", (event) => {
      event.preventDefault();
      if (!state.currentResult || !state.currentResult.quiz) {
        return;
      }

      const checkedRadio = quizOptionsList.querySelector('input[name="quiz-option"]:checked');
      if (!checkedRadio) {
        return;
      }

      const chosenIndex = Number.parseInt(checkedRadio.value, 10);
      const correctIndex = state.currentResult.quiz.correct_index;
      const isCorrect = chosenIndex === correctIndex;
      const isUrdu = state.currentResult.language === "ur";

      const labels = Array.from(quizOptionsList.querySelectorAll(".quiz-option-label"));
      labels.forEach((lbl, idx) => {
        lbl.classList.remove("is-correct", "is-incorrect");
        if (idx === correctIndex) {
          lbl.classList.add("is-correct");
        } else if (idx === chosenIndex && !isCorrect) {
          lbl.classList.add("is-incorrect");
        }
      });

      quizFeedbackBox.classList.remove("hidden", "is-correct", "is-incorrect");
      quizFeedbackBox.classList.add(isCorrect ? "is-correct" : "is-incorrect");

      if (isCorrect) {
        quizFeedbackStatus.textContent = isUrdu
          ? "درست جواب! (Correct)"
          : "Correct answer!";
      } else {
        quizFeedbackStatus.textContent = isUrdu
          ? "یہ جواب درست نہیں ہے۔ صحیح وضاحت نیچے دیکھیں:"
          : "Not quite right. Here is why:";
      }

      quizFeedbackText.textContent = state.currentResult.quiz.feedback;
    });
  }

  // Event Listeners: Browser Speech Synthesis
  if ("speechSynthesis" in window) {
    window.speechSynthesis.onvoiceschanged = () => {
      if (state.currentResult) {
        updateSpeechAvailability(state.currentResult.language);
      }
    };
  }

  if (listenBtn) {
    listenBtn.addEventListener("click", () => {
      if (!state.currentResult || !("speechSynthesis" in window)) {
        return;
      }
      stopSpeech();

      const langCode = state.currentResult.language;
      const voice = getMatchingVoice(langCode);
      if (!voice) {
        updateSpeechAvailability(langCode);
        return;
      }

      const textToRead = [
        state.currentResult.explanation,
        ...(state.currentResult.key_points || []),
      ].join(". ");

      const utterance = new SpeechSynthesisUtterance(textToRead);
      utterance.lang = langCode === "ur" ? "ur-PK" : "en-US";
      if (voice) {
        utterance.voice = voice;
      }

      utterance.onend = () => {
        stopAudioBtn.classList.add("hidden");
        listenBtnLabel.textContent = "Listen";
      };
      utterance.onerror = () => {
        stopAudioBtn.classList.add("hidden");
        listenBtnLabel.textContent = "Listen";
      };

      stopAudioBtn.classList.remove("hidden");
      listenBtnLabel.textContent = "Playing...";
      window.speechSynthesis.speak(utterance);
    });
  }

  if (stopAudioBtn) {
    stopAudioBtn.addEventListener("click", stopSpeech);
  }

  // Event Listener: Direct / Constrained Follow-Up Question
  if (followupForm) {
    followupForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const targetTopicId =
        (state.currentResult && state.currentResult.topic_id) || state.selectedTopicId;
      const targetLanguage =
        (state.currentResult && state.currentResult.language) || state.selectedLanguage;

      const questionText = (followupInput.value || "").trim();
      if (!questionText) {
        followupError.textContent =
          targetLanguage === "ur"
            ? "براہِ کرم اپنا سوال درج کریں۔"
            : "Please enter a short question about this topic.";
        followupError.classList.remove("hidden");
        return;
      }

      const requestId = ++state.activeFollowupRequestId;
      followupError.classList.add("hidden");
      followupResult.classList.add("hidden");
      followupLoading.classList.remove("hidden");
      followupSubmitBtn.disabled = true;

      try {
        const response = await fetch("/api/ask", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            topic_id: targetTopicId,
            language: targetLanguage,
            question: questionText,
          }),
        });

        const payload = await response.json();
        if (requestId !== state.activeFollowupRequestId) {
          return;
        }
        followupLoading.classList.add("hidden");
        followupSubmitBtn.disabled = false;

        if (!response.ok || payload.error) {
          followupError.textContent =
            payload && payload.error && payload.error.message
              ? payload.error.message
              : "Live AI couldn't answer right now. Please try again.";
          followupError.classList.remove("hidden");
          return;
        }

        const isUrdu = payload.language === "ur";
        followupAnswerText.setAttribute("lang", isUrdu ? "ur" : "en");
        followupAnswerText.setAttribute("dir", isUrdu ? "rtl" : "ltr");
        followupAnswerText.textContent = payload.answer;

        followupBadge.className = "badge";
        if (payload.boundary_triggered) {
          followupBadge.classList.add("badge--warning");
          followupBadge.textContent = "Safety Scope Boundary (Educational Tool Only)";
        } else if (payload.supported_by_source) {
          followupBadge.classList.add("badge--live");
          followupBadge.textContent = "Verified Live AI (Grounded in CDC Facts)";
        } else {
          followupBadge.classList.add("badge--neutral");
          followupBadge.textContent = "Outside Current Topic Facts";
        }

        if (followupSourceNote && payload.source && payload.source.title) {
          followupSourceNote.textContent = `Source: ${payload.source.title}`;
        }

        followupResult.classList.remove("hidden");
      } catch {
        if (requestId !== state.activeFollowupRequestId) {
          return;
        }
        followupLoading.classList.add("hidden");
        followupSubmitBtn.disabled = false;
        followupError.textContent =
          "Could not reach the server. Please check your connection and try again.";
        followupError.classList.remove("hidden");
      }
    });
  }

  // Initialize UI
  updateSelectionUI();
  checkAiConfiguration();
})();
