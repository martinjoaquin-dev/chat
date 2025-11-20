import { Injectable } from '@angular/core';
import { HttpClient, HttpEvent, HttpEventType } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface FileInfo {
  filename: string;
  size: number;
  uploaded_at: string;
  signed: boolean;
}

export interface FileListResponse {
  files: FileInfo[];
  count: number;
  warning?: string;
  error?: string;
}

export interface VerifyResponse {
  valid: boolean;
  message: string;
  timestamp?: string;
}

@Injectable({
  providedIn: 'root'
})
export class FileService {
  private apiUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  listFiles(): Observable<FileListResponse> {
    return this.http.get<FileListResponse>(`${this.apiUrl}/files`);
  }

  uploadFile(file: File, signerName?: string, signerEmail?: string): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    
    if (signerName) {
      formData.append('signer_name', signerName);
    }
    if (signerEmail) {
      formData.append('signer_email', signerEmail);
    }
    
    return this.http.post(`${this.apiUrl}/files/upload`, formData, {
      reportProgress: true,
      observe: 'events',
      responseType: 'json'
    });
  }

  verifySignature(filename: string): Observable<VerifyResponse> {
    return this.http.post<VerifyResponse>(`${this.apiUrl}/files/verify`, {
      filename
    });
  }
}

