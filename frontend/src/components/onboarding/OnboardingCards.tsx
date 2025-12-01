/**
 * Onboarding Cards Component
 * Shows helpful cue cards for new users explaining what the app does and how to use it
 */

import { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';

interface Card {
  id: number;
  icon: string;
  title: string;
  description: string;
  steps?: string[];
}

const cards: Card[] = [
  {
    id: 1,
    icon: '🎤',
    title: 'Record or Upload Audio',
    description: 'Start by recording a consultation directly in your browser or uploading an audio file (MP3, WAV, WebM)',
    steps: [
      'Click "Record Audio" to start recording',
      'Or click "Upload Audio File" to select a file',
      'Speak in Tamil or Telugu during the consultation'
    ]
  },
  {
    id: 2,
    icon: '🔊',
    title: 'AI Transcription',
    description: 'Our AI automatically transcribes your audio in real-time, separating doctor and patient speech',
    steps: [
      'Upload completes automatically',
      'AI processes the audio (15-40 seconds)',
      'Transcription appears in structured format'
    ]
  },
  {
    id: 3,
    icon: '📝',
    title: 'SOAP Note Generation',
    description: 'Get professional medical SOAP notes with Subjective, Objective, Assessment, and Plan sections',
    steps: [
      'AI extracts symptoms, medications, diagnoses',
      'Generates ICD-10 codes automatically',
      'Creates structured SOAP note in English'
    ]
  },
  {
    id: 4,
    icon: '✏️',
    title: 'Review & Edit',
    description: 'Review the generated SOAP note, make edits if needed, and approve before finalizing',
    steps: [
      'Click "Edit SOAP Note" to make changes',
      'Review all sections carefully',
      'Click "Approve & Finalize" when ready'
    ]
  },
  {
    id: 5,
    icon: '📄',
    title: 'Download PDF',
    description: 'Export your approved SOAP notes as professional PDF documents for patient records',
    steps: [
      'After approval, click "Download PDF"',
      'PDF includes transcript, SOAP note, and entities',
      'Save to your records or EHR system'
    ]
  }
];

export default function OnboardingCards() {
  const [currentCard, setCurrentCard] = useState(0);
  const [isDismissed, setIsDismissed] = useState(false);
  const [shouldShow, setShouldShow] = useState(false);
  const { user } = useAuth();

  // Check localStorage only once on mount and set initial state
  useEffect(() => {
    if (!user) {
      setShouldShow(false);
      return;
    }

    // Use user-specific localStorage key
    const storageKey = `medscribe_onboarding_seen_${user.id}`;
    const hasSeenOnboarding = localStorage.getItem(storageKey) === 'true';
    
    // Show cards if user hasn't dismissed them
    // Default to showing for new users (if flag doesn't exist)
    setShouldShow(!hasSeenOnboarding);
  }, [user]);

  // Don't render if dismissed, already seen, or user not loaded
  if (isDismissed || !shouldShow || !user) {
    return null;
  }

  const handleDismiss = () => {
    setIsDismissed(true);
    if (user) {
      // Use user-specific localStorage key
      const storageKey = `medscribe_onboarding_seen_${user.id}`;
      localStorage.setItem(storageKey, 'true');
    }
  };

  const handleNext = () => {
    if (currentCard < cards.length - 1) {
      setCurrentCard(currentCard + 1);
    } else {
      handleDismiss();
    }
  };

  const handlePrevious = () => {
    if (currentCard > 0) {
      setCurrentCard(currentCard - 1);
    }
  };

  const card = cards[currentCard];

  return (
    <div className="mb-8 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg shadow-lg border border-blue-200 overflow-hidden">
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-3xl">{card.icon}</span>
              <h3 className="text-xl font-bold text-gray-900">{card.title}</h3>
            </div>
            <p className="text-gray-600 text-sm">{card.description}</p>
          </div>
          <button
            onClick={handleDismiss}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            aria-label="Dismiss"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Steps */}
        {card.steps && (
          <div className="mt-4 space-y-2">
            {card.steps.map((step, index) => (
              <div key={index} className="flex items-start gap-2 text-sm text-gray-700">
                <span className="flex-shrink-0 w-5 h-5 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xs font-semibold mt-0.5">
                  {index + 1}
                </span>
                <span>{step}</span>
              </div>
            ))}
          </div>
        )}

        {/* Navigation */}
        <div className="mt-6 flex items-center justify-between">
          <div className="flex items-center gap-2">
            {cards.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentCard(index)}
                className={`h-2 rounded-full transition-all ${
                  index === currentCard ? 'w-8 bg-blue-600' : 'w-2 bg-gray-300'
                }`}
                aria-label={`Go to step ${index + 1}`}
              />
            ))}
          </div>
          <div className="flex items-center gap-2">
            {currentCard > 0 && (
              <button
                onClick={handlePrevious}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Previous
              </button>
            )}
            <button
              onClick={handleNext}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
            >
              {currentCard === cards.length - 1 ? 'Get Started' : 'Next'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

