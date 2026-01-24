import type { ContactMessageRequest, ContactSubmitResponse } from '@/types/contact';

const API_URL = typeof window !== 'undefined' 
  ? (window as unknown as { ENV?: { API_URL?: string } }).ENV?.API_URL || 'http://localhost:8000'
  : 'http://localhost:8000';

const CONTACT_ENDPOINT = `${API_URL}/api/contact/`;

export const contactAPI = {
  /**
   * Send a contact message to the admin team.
   * Requires authentication - the user is identified from the JWT token.
   * 
   * @param data - The message data (subject and message)
   * @returns Promise with success message and created message data
   */
  sendMessage: async (data: ContactMessageRequest): Promise<ContactSubmitResponse> => {
    const response = await fetch(CONTACT_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // Important: sends cookies with request
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      
      if (response.status === 401) {
        throw new Error('You must be logged in to send a message.');
      }
      
      // Handle validation errors
      if (errorData.subject) {
        throw new Error(errorData.subject[0] || 'Invalid subject.');
      }
      if (errorData.message) {
        throw new Error(errorData.message[0] || 'Invalid message.');
      }
      
      throw new Error('Failed to send message. Please try again.');
    }

    return response.json();
  },
};
