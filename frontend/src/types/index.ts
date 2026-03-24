/**
 * Response structure when uploading a document to the backend.
 */
export interface UploadResponse {
  success: boolean;
  source: string;
  chunks_stored: number;
  message: string;
}

/**
 * Citation indicating where a piece of information was found in the source documents.
 */
export interface Citation {
  source: string;
  type: 'pdf' | 'youtube';
  page?: number;
  timestamp?: string;
}

/**
 * Response structure when sending a chat query to the assistant.
 */
export interface ChatResponse {
  answer: string;
  citations: Citation[];
  chunks_used: number;
  response_time_ms: number;
  error: string | null;
}

/**
 * Structure containing all stored sources in the backend.
 */
export interface SourcesResponse {
  sources: string[];
}

/**
 * Represents a chat message in the UI, containing either the user's query or the assistant's context-aware response.
 */
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  timestamp: Date;
  isLoading?: boolean;
  error?: string | null;
  response_time_ms?: number;
  chunks_used?: number;
}

/**
 * Toast message for displaying brief UI notifications.
 */
export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'loading' | 'info';
  message: string;
  duration?: number;
}

/**
 * Status tracking state for document uploads.
 */
export interface UploadStatus {
  isUploading: boolean;
  progress: 'idle' | 'uploading' | 'processing' | 'success' | 'error';
  message: string;
  source?: string;
}

/**
 * Function type for sending a new message to the chat.
 */
export type SendMessageFn = (message: string) => Promise<void>;

/**
 * Function type for deleting an existing document source from the backend.
 */
export type DeleteSourceFn = (source: string) => Promise<void>;
