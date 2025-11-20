import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';

export interface Message {
  id?: string;
  content: string;
  sender: string;
  recipient?: string;
  timestamp: string;
  encrypted?: boolean;
}

export interface ChatStatus {
  running: boolean;
  host: string;
  port: number;
  clients_connected: number;
}

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private apiUrl = 'http://localhost:8000/api';
  private messagesSubject = new BehaviorSubject<Message[]>([]);
  public messages$ = this.messagesSubject.asObservable();

  constructor(private http: HttpClient) {}

  getStatus(): Observable<ChatStatus> {
    return this.http.get<ChatStatus>(`${this.apiUrl}/chat/status`);
  }

  sendMessage(message: string, recipient?: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/chat/send`, {
      message,
      recipient
    });
  }

  getMessages(): Observable<{ messages: Message[], count: number }> {
    return this.http.get<{ messages: Message[], count: number }>(`${this.apiUrl}/chat/messages`);
  }

  loadAndUpdateMessages(): void {
    this.getMessages().subscribe({
      next: (response) => {
        if (response.messages && response.messages.length > 0) {
          this.messagesSubject.next(response.messages);
        }
      },
      error: (error) => {
        console.error('Error loading messages:', error);
      }
    });
  }

  addMessage(message: Message): void {
    const current = this.messagesSubject.value;
    this.messagesSubject.next([...current, message]);
  }

  clearMessages(): void {
    this.messagesSubject.next([]);
  }

  clearChatHistory(): Observable<any> {
    return this.http.delete(`${this.apiUrl}/chat/messages`);
  }
}

