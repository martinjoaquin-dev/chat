import { Component, OnInit } from '@angular/core';
import { FileService, FileInfo } from '../../services/file.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-files',
  templateUrl: './files.component.html',
  styleUrls: ['./files.component.scss']
})
export class FilesComponent implements OnInit {
  files: FileInfo[] = [];
  loading = false;
  uploading = false;
  uploadProgress = 0;

  constructor(
    private fileService: FileService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadFiles();
  }

  loadFiles(): void {
    this.loading = true;
    this.fileService.listFiles().subscribe({
      next: (response) => {
        this.files = response.files || [];
        this.loading = false;
        
        // Mostrar advertencia si hay algún problema
        if (response.warning) {
          this.snackBar.open(response.warning, 'Cerrar', {
            duration: 5000,
            panelClass: ['warning-snackbar'],
            verticalPosition: 'top',
            horizontalPosition: 'end'
          });
        }
      },
      error: (error) => {
        console.error('Error loading files:', error);
        this.loading = false;
        this.snackBar.open('No se pudieron cargar los archivos. Intenta nuevamente.', 'Cerrar', {
          duration: 4000,
          panelClass: ['error-snackbar'],
          verticalPosition: 'top',
          horizontalPosition: 'end'
        });
      }
    });
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      const file = input.files[0];
      this.uploadFile(file);
    }
  }

  uploadFile(file: File): void {
    this.uploading = true;
    this.uploadProgress = 0;

    this.fileService.uploadFile(file).subscribe({
      next: (event: any) => {
        if (event.type === 'uploadProgress') {
          this.uploadProgress = Math.round((event.loaded / event.total) * 100);
        } else if (event.type === 'response') {
          this.uploading = false;
          this.uploadProgress = 0;
          const response = event.body;
          if (response && response.success) {
            this.snackBar.open('Archivo subido y firmado digitalmente con éxito', 'Cerrar', {
              duration: 4000,
              panelClass: ['success-snackbar'],
              verticalPosition: 'top',
              horizontalPosition: 'end'
            });
          } else {
            this.snackBar.open('Archivo subido exitosamente', 'Cerrar', {
              duration: 3000,
              panelClass: ['success-snackbar'],
              verticalPosition: 'top',
              horizontalPosition: 'end'
            });
          }
          this.loadFiles();
        }
      },
      error: (error) => {
        this.uploading = false;
        this.uploadProgress = 0;
        const errorMessage = error?.error?.detail || error?.message || 'Error desconocido';
        this.snackBar.open(`Error al subir archivo: ${errorMessage}`, 'Cerrar', {
          duration: 5000,
          panelClass: ['error-snackbar'],
          verticalPosition: 'top',
          horizontalPosition: 'end'
        });
      }
    });
  }

  verifySignature(file: FileInfo): void {
    this.fileService.verifySignature(file.filename).subscribe({
      next: (response) => {
        if (response.valid) {
          this.snackBar.open('Firma digital válida. El archivo no ha sido modificado.', 'Cerrar', {
            duration: 4000,
            panelClass: ['success-snackbar'],
            verticalPosition: 'top',
            horizontalPosition: 'end'
          });
        } else {
          this.snackBar.open('Firma digital inválida. El archivo puede haber sido alterado.', 'Cerrar', {
            duration: 4000,
            panelClass: ['error-snackbar'],
            verticalPosition: 'top',
            horizontalPosition: 'end'
          });
        }
      },
      error: (error) => {
        const errorMessage = error?.error?.detail || error?.message || 'Error desconocido';
        this.snackBar.open(`No se pudo verificar la firma: ${errorMessage}`, 'Cerrar', {
          duration: 4000,
          panelClass: ['error-snackbar'],
          verticalPosition: 'top',
          horizontalPosition: 'end'
        });
      }
    });
  }

  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleString('es-ES');
  }

  getFileIcon(filename: string): string {
    const ext = filename.split('.').pop()?.toLowerCase();
    switch (ext) {
      case 'pdf':
        return 'picture_as_pdf';
      case 'txt':
        return 'text_snippet';
      case 'zip':
        return 'folder_zip';
      default:
        return 'insert_drive_file';
    }
  }
}

