import axios from 'axios';
import type {
  UploadResponse,
  SourcesResponse,
  ChatResponse,
} from '../types/index';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

// Normalize all axios errors into plain Error objects
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ??
      error.response?.data?.message ??
      error.message;
    throw new Error(message);
  },
);

/**
 * Upload a PDF file to the backend for RAG ingestion.
 * @param file - The PDF file to upload.
 * @returns The upload result including source name and chunk count.
 */
export async function uploadPDF(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post<UploadResponse>('/upload/pdf', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

/**
 * Submit a YouTube URL for transcript extraction and RAG ingestion.
 * @param url - The YouTube video URL.
 * @returns The upload result including source name and chunk count.
 */
export async function uploadYoutube(url: string): Promise<UploadResponse> {
  const { data } = await api.post<UploadResponse>('/upload/youtube', { url });
  return data;
}

/**
 * Retrieve the list of all ingested source names.
 * @returns An array of source name strings.
 */
export async function getSources(): Promise<string[]> {
  const { data } = await api.get<SourcesResponse>('/upload/sources');
  return data.sources;
}

/**
 * Delete a previously ingested source and its chunks.
 * @param sourceName - The name of the source to delete (may contain slashes for YouTube URLs).
 */
export async function deleteSource(sourceName: string): Promise<void> {
  await api.delete(`/upload/source/${encodeURIComponent(sourceName)}`);
}

/**
 * Send a question to the RAG assistant and receive a cited answer.
 * @param question - The user's natural-language question.
 * @param topK - Number of top chunks to retrieve (defaults to 6).
 * @returns The assistant's answer with citations and metadata.
 */
export async function askQuestion(
  question: string,
  topK: number = 6,
): Promise<ChatResponse> {
  const { data } = await api.post<ChatResponse>('/chat/ask', {
    question,
    top_k: topK,
  });
  return data;
}
