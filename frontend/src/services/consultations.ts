/**
 * Consultations Service
 */

import api from './api';

export interface Consultation {
  id: string;
  status: 'processing' | 'review' | 'completed' | 'failed';
  patient_name?: string;
  language: string;
  transcript?: string;
  soap_note?: any;
  entities?: {
    symptoms: string[];
    medications: string[];
    diagnoses: string[];
    vitals: Record<string, string>;
  };
  icd_codes?: string[];
  cost?: number;
  created_at: string;
  completed_at?: string;
  review_status?: 'pending_review' | 'under_review' | 'approved' | 'rejected';
  reviewed_by?: string;
  reviewed_at?: string;
  approved_by?: string;
  approved_at?: string;
  edit_count?: number;
}

export interface CreateConsultationRequest {
  file: File;
  language: 'ta' | 'te';
  patient_name?: string;
}

export interface CreateConsultationResponse {
  id: string;
  status: 'processing';
  patient_name?: string;
  language: string;
  poll_url: string;
  estimated_time?: number;
  created_at: string;
}

export const consultationsService = {
  async create(data: CreateConsultationRequest): Promise<CreateConsultationResponse> {
    const formData = new FormData();
    formData.append('file', data.file);
    formData.append('language', data.language);
    if (data.patient_name) {
      formData.append('patient_name', data.patient_name);
    }

    const response = await api.post<CreateConsultationResponse>(
      '/consultations',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  async getById(id: string): Promise<Consultation> {
    const response = await api.get<Consultation>(`/consultations/${id}`);
    return response.data;
  },

  async list(): Promise<Consultation[]> {
    const response = await api.get<{consultations: Consultation[], count: number}>('/consultations');
    return response.data.consultations || [];
  },

  async downloadPDF(id: string): Promise<Blob> {
    const response = await api.get(`/consultations/${id}/pdf`, {
      responseType: 'blob',
    });
    return response.data;
  },

  async updateReview(id: string, reviewData: {
    soap_note: any;
    entities?: any;
    icd_codes?: string[];
    edit_reason?: string;
  }): Promise<Consultation> {
    const response = await api.put<Consultation>(`/consultations/${id}/review`, reviewData);
    return response.data;
  },

  async approveConsultation(id: string, reviewNotes?: string): Promise<Consultation> {
    const response = await api.post<Consultation>(`/consultations/${id}/approve`, {
      review_notes: reviewNotes
    });
    return response.data;
  },

  async getEditHistory(id: string): Promise<any[]> {
    const response = await api.get<{edit_history: any[], count: number}>(`/consultations/${id}/edit-history`);
    return response.data.edit_history || [];
  },
};

