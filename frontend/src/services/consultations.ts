/**
 * Consultations Service
 */

import api from './api';

export interface Consultation {
  id: string;
  status: 'processing' | 'completed' | 'failed';
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
};

