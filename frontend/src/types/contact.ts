export interface ContactMessageRequest {
  subject: string;
  message: string;
}

export interface ContactMessageResponse {
  id: number;
  subject: string;
  message: string;
  status: 'pending' | 'responded';
  created_at: string;
}

export interface ContactSubmitResponse {
  message: string;
  data: ContactMessageResponse;
}
