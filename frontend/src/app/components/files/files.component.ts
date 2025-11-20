import { Component, OnInit } from '@angular/core';
import { FileService, FileInfo } from '../../services/file.service';
import { AuthService } from '../../services/auth.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatDialog } from '@angular/material/dialog';
import { SignDialogComponent } from './sign-dialog.component';
import { DomSanitizer, SafeUrl } from '@angular/platform-browser';

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
  selectedFile: File | null = null;

  constructor(
    private fileService: FileService,
    private authService: AuthService,
    private snackBar: MatSnackBar,
    private dialog: MatDialog,
    private sanitizer: DomSanitizer
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
      this.selectedFile = file;
      this.showSignDialog(file);
    }
  }

  showSignDialog(file: File): void {
    // Obtener información del usuario OAuth o tradicional
    const userName = this.authService.getUsername() || this.authService.getEmail() || 'Usuario';
    const userEmail = this.authService.getEmail() || undefined; // Convertir null a undefined

    const dialogRef = this.dialog.open(SignDialogComponent, {
      width: '500px',
      data: {
        filename: file.name,
        userName: userName,
        userEmail: userEmail
      },
      disableClose: true
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result === true) {
        // Usuario confirmó, proceder con la firma
        this.uploadFile(file, userName, userEmail);
      } else {
        // Usuario canceló
        this.selectedFile = null;
        // Resetear el input file
        const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
        if (fileInput) {
          fileInput.value = '';
        }
      }
    });
  }

  uploadFile(file: File, signerName?: string, signerEmail?: string): void {
    // Mostrar estado inicial
    this.snackBar.open('📤 Subiendo archivo...', '', {
      duration: 3000,
      panelClass: ['info-snackbar'],
      verticalPosition: 'top',
      horizontalPosition: 'end'
    });
    
    this.uploading = true;
    this.uploadProgress = 5; // Iniciar con 5% para mostrar que está empezando

    // Simular progreso inicial mientras se inicia la subida
    const progressInterval = setInterval(() => {
      if (this.uploadProgress < 15 && this.uploading) {
        this.uploadProgress += 2;
      }
    }, 200);

    this.fileService.uploadFile(file, signerName, signerEmail).subscribe({
      next: (event: any) => {
        console.log('Evento recibido:', event); // DEBUG
        
        // Detener el intervalo cuando empezamos a recibir eventos reales
        if (event.type === 1 || event.type === 4) { // HttpEventType.UploadProgress o HttpEventType.Response
          clearInterval(progressInterval);
        }

        // HttpEventType.UploadProgress = 1
        if (event.type === 1 && event.loaded && event.total) {
          // Progreso real de la subida (hasta 90%)
          const uploadPercent = Math.round((event.loaded / event.total) * 90);
          this.uploadProgress = Math.max(this.uploadProgress, uploadPercent);
          console.log('Progreso:', uploadPercent + '%'); // DEBUG
        } 
        // HttpEventType.Response = 4
        else if (event.type === 4) {
          // ¡RESPUESTA RECIBIDA! Completar inmediatamente y refrescar
          clearInterval(progressInterval);
          this.uploadProgress = 100;
          
          console.log('Respuesta recibida:', event.body); // DEBUG
          
          const response = event.body;
          const signerName = response?.signer_name || 'Usuario';
          
          // REFRESCAR LISTA INMEDIATAMENTE (ANTES DE TODO)
          this.loadFiles();
          
          // Ocultar barra de progreso inmediatamente
          setTimeout(() => {
            this.uploading = false;
            this.uploadProgress = 0;
            this.selectedFile = null;
          }, 300); // Pequeña animación antes de ocultar
          
          // Mostrar mensaje de éxito
          if (response && response.success) {
            this.snackBar.open(`✅ Archivo firmado digitalmente por ${signerName}`, 'Cerrar', {
              duration: 5000,
              panelClass: ['success-snackbar'],
              verticalPosition: 'top',
              horizontalPosition: 'end'
            });
            
            // Descargar el archivo firmado si está disponible
            if (response.signed_file_url) {
              setTimeout(() => {
                const downloadFilename = response.signed_filename || response.filename;
                this.downloadSignedFile(response.signed_file_url, downloadFilename);
              }, 500);
            }
          } else {
            this.snackBar.open('✅ Archivo subido exitosamente', 'Cerrar', {
              duration: 3000,
              panelClass: ['success-snackbar'],
              verticalPosition: 'top',
              horizontalPosition: 'end'
            });
          }
        }
        // Manejar también si viene como string (por compatibilidad)
        else if (event.type === 'uploadProgress') {
          const uploadPercent = Math.round((event.loaded / event.total) * 90);
          this.uploadProgress = Math.max(this.uploadProgress, uploadPercent);
        } else if (event.type === 'response') {
          clearInterval(progressInterval);
          this.uploadProgress = 100;
          
          const response = event.body;
          const signerName = response?.signer_name || 'Usuario';
          
          this.loadFiles();
          
          setTimeout(() => {
            this.uploading = false;
            this.uploadProgress = 0;
            this.selectedFile = null;
          }, 300);
          
          if (response && response.success) {
            this.snackBar.open(`✅ Archivo firmado digitalmente por ${signerName}`, 'Cerrar', {
              duration: 5000,
              panelClass: ['success-snackbar'],
              verticalPosition: 'top',
              horizontalPosition: 'end'
            });
            
            if (response.signed_file_url) {
              setTimeout(() => {
                const downloadFilename = response.signed_filename || response.filename;
                this.downloadSignedFile(response.signed_file_url, downloadFilename);
              }, 500);
            }
          }
        }
      },
      error: (error) => {
        console.error('Error en upload:', error); // DEBUG
        clearInterval(progressInterval);
        this.uploading = false;
        this.uploadProgress = 0;
        this.selectedFile = null;
        
        // Refrescar lista de archivos incluso si hay error (por si acaso se subió parcialmente)
        this.loadFiles();
        
        const errorMessage = error?.error?.detail || error?.message || 'Error desconocido';
        console.error('Mensaje de error:', errorMessage); // DEBUG
        this.snackBar.open(`❌ Error al subir archivo: ${errorMessage}`, 'Cerrar', {
          duration: 6000,
          panelClass: ['error-snackbar'],
          verticalPosition: 'top',
          horizontalPosition: 'end'
        });
      },
      complete: () => {
        console.log('Upload observable completado'); // DEBUG
        clearInterval(progressInterval);
        // Si llegamos aquí sin response, forzar refresh
        if (this.uploading) {
          console.log('Forzando refresh porque upload sigue activo'); // DEBUG
          this.loadFiles();
          setTimeout(() => {
            this.uploading = false;
            this.uploadProgress = 0;
            this.selectedFile = null;
          }, 300);
        }
      }
    });
  }

  downloadSignedFile(fileUrl: string, filename: string): void {
    // Descargar el archivo firmado
    const link = document.createElement('a');
    link.href = fileUrl;
    link.download = filename;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    this.snackBar.open('Archivo firmado descargado', 'Cerrar', {
      duration: 3000,
      panelClass: ['success-snackbar'],
      verticalPosition: 'top',
      horizontalPosition: 'end'
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

