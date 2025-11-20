import { Injectable } from '@angular/core';
import { HttpClient, HttpEvent } from '@angular/common/http';
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

  uploadFile(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    
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

