/**
 * Consultation Detail Page
 */

import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { consultationsService, Consultation } from '../services/consultations';

export default function ConsultationDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [consultation, setConsultation] = useState<Consultation | null>(null);
  const [loading, setLoading] = useState(true);
  const [, setPolling] = useState(false);

  useEffect(() => {
    if (!id) return;
    
    // Initial load
    loadConsultation();
  }, [id]);

  // Separate effect for polling
  useEffect(() => {
    if (!consultation || consultation.status !== 'processing') {
      setPolling(false);
      return;
    }

    // Start polling if processing
    setPolling(true);
    const interval = setInterval(() => {
      loadConsultation();
    }, 3000); // Poll every 3 seconds

    return () => {
      clearInterval(interval);
      setPolling(false);
    };
  }, [consultation?.status, id]);

  const loadConsultation = async () => {
    if (!id) return;
    try {
      const data = await consultationsService.getById(id);
      const previousStatus = consultation?.status;
      
      setConsultation(data);
      setLoading(false);
      
      // Show toast when status changes
      if (previousStatus === 'processing' && data.status === 'completed') {
        toast.success('Consultation processing completed!');
      } else if (previousStatus === 'processing' && data.status === 'failed') {
        toast.error('Consultation processing failed. Please try again.');
      }
    } catch (error: any) {
      console.error('Failed to load consultation:', error);
      toast.error(error.response?.data?.detail || 'Failed to load consultation');
      if (error.response?.status === 404) {
        setTimeout(() => navigate('/dashboard'), 2000);
      }
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading consultation...</p>
        </div>
      </div>
    );
  }

  if (!consultation) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4">Consultation not found</h2>
          <Link to="/dashboard" className="text-blue-600 hover:underline">
            Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'processing':
        return 'bg-yellow-100 text-yellow-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-4">
          <Link
            to="/dashboard"
            className="text-blue-600 hover:text-blue-800 font-medium"
          >
            ← Back to Dashboard
          </Link>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Consultation Details
              </h1>
              <p className="text-gray-600 mt-2">
                Patient: {consultation.patient_name || 'Not provided'} | Language:{' '}
                {consultation.language === 'ta' ? 'Tamil' : 'Telugu'}
              </p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={loadConsultation}
                disabled={loading}
                className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
                title="Refresh consultation data"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Refresh
              </button>
              <span
                className={`px-3 py-1 text-sm font-semibold rounded-full ${getStatusColor(
                  consultation.status
                )}`}
              >
                {consultation.status}
              </span>
            </div>
          </div>

          {consultation.status === 'processing' && (
            <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded mb-4">
              Processing... This may take 15-40 seconds.
            </div>
          )}
        </div>

        {consultation.status === 'completed' && (
          <>
            {/* Transcript */}
            {consultation.transcript && (
              <div className="bg-white rounded-lg shadow-md p-6 mb-6">
                <h2 className="text-2xl font-bold mb-4">Transcript</h2>
                <div className="bg-gray-50 p-4 rounded border">
                  <p className="whitespace-pre-wrap">{consultation.transcript}</p>
                </div>
              </div>
            )}

            {/* SOAP Note */}
            {consultation.soap_note && (
              <div className="bg-white rounded-lg shadow-md p-6 mb-6">
                <h2 className="text-2xl font-bold mb-4">SOAP Note</h2>
                {typeof consultation.soap_note === 'string' ? (
                  <div
                    className="prose max-w-none"
                    dangerouslySetInnerHTML={{
                      __html: consultation.soap_note.replace(/\n/g, '<br />'),
                    }}
                  />
                ) : consultation.soap_note.markdown ? (
                  <div
                    className="prose max-w-none"
                    dangerouslySetInnerHTML={{
                      __html: consultation.soap_note.markdown.replace(/\n/g, '<br />'),
                    }}
                  />
                ) : (
                  <div className="space-y-4">
                    {consultation.soap_note.subjective && (
                      <div>
                        <h3 className="font-bold text-lg">Subjective</h3>
                        <p className="text-gray-700">
                          {consultation.soap_note.subjective}
                        </p>
                      </div>
                    )}
                    {consultation.soap_note.objective && (
                      <div>
                        <h3 className="font-bold text-lg">Objective</h3>
                        <p className="text-gray-700">
                          {consultation.soap_note.objective}
                        </p>
                      </div>
                    )}
                    {consultation.soap_note.assessment && (
                      <div>
                        <h3 className="font-bold text-lg">Assessment</h3>
                        <p className="text-gray-700">
                          {consultation.soap_note.assessment}
                        </p>
                      </div>
                    )}
                    {consultation.soap_note.plan && (
                      <div>
                        <h3 className="font-bold text-lg">Plan</h3>
                        <p className="text-gray-700">
                          {consultation.soap_note.plan}
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Entities */}
            {consultation.entities && (
              <div className="bg-white rounded-lg shadow-md p-6 mb-6">
                <h2 className="text-2xl font-bold mb-4">Extracted Entities</h2>
                <div className="grid grid-cols-2 gap-4">
                  {consultation.entities.symptoms?.length > 0 && (
                    <div>
                      <h3 className="font-semibold mb-2">Symptoms</h3>
                      <ul className="list-disc list-inside">
                        {consultation.entities.symptoms.map((s, i) => (
                          <li key={i}>{s}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {consultation.entities.medications?.length > 0 && (
                    <div>
                      <h3 className="font-semibold mb-2">Medications</h3>
                      <ul className="list-disc list-inside">
                        {consultation.entities.medications.map((m, i) => (
                          <li key={i}>{m}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {consultation.entities.diagnoses?.length > 0 && (
                    <div>
                      <h3 className="font-semibold mb-2">Diagnoses</h3>
                      <ul className="list-disc list-inside">
                        {consultation.entities.diagnoses.map((d, i) => (
                          <li key={i}>{d}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="bg-white rounded-lg shadow-md p-6 flex gap-4">
              <button
                onClick={async () => {
                  try {
                    toast.loading('Generating PDF...');
                    const blob = await consultationsService.downloadPDF(consultation.id);
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `consultation_${consultation.patient_name || consultation.id}.pdf`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                    toast.dismiss();
                    toast.success('PDF downloaded successfully!');
                  } catch (error: any) {
                    toast.dismiss();
                    toast.error(error.response?.data?.detail || 'Failed to download PDF');
                  }
                }}
                className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 flex items-center gap-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Download PDF
              </button>
              
              {consultation.cost && (
                <div className="flex items-center text-gray-600">
                  <span className="font-medium">Processing Cost: ₹{consultation.cost.toFixed(2)}</span>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

