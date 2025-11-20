import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

export interface SignDialogData {
  filename: string;
  userName?: string;
  userEmail?: string;
}

@Component({
  selector: 'app-sign-dialog',
  template: `
    <div class="dialog-container">
      <div class="dialog-header">
        <mat-icon class="header-icon">verified</mat-icon>
        <h2 mat-dialog-title>Confirmar Firma Digital</h2>
      </div>
      
      <mat-dialog-content>
        <div class="dialog-content">
          <div class="info-section">
            <mat-icon class="info-icon">info</mat-icon>
            <p class="info-text">
              Al aceptar, <strong>su nombre será validado como firma digital</strong> en el documento.
            </p>
          </div>
          
          <div class="details-section">
            <div class="detail-item">
              <mat-icon class="detail-icon">description</mat-icon>
              <div class="detail-content">
                <span class="detail-label">Archivo</span>
                <span class="detail-value">{{ data.filename }}</span>
              </div>
            </div>
            
            <div class="detail-item" *ngIf="data.userName || data.userEmail">
              <mat-icon class="detail-icon">person</mat-icon>
              <div class="detail-content">
                <span class="detail-label">Firmante</span>
                <span class="detail-value">
                  {{ data.userName || data.userEmail }}
                  <span class="detail-email" *ngIf="data.userEmail && data.userName">({{ data.userEmail }})</span>
                </span>
              </div>
            </div>
          </div>
          
          <div class="acceptance-section" [class.accepted]="accepted">
            <mat-checkbox [(ngModel)]="accepted" class="accept-checkbox">
              Confirmo que acepto firmar este documento con mi nombre
            </mat-checkbox>
          </div>
        </div>
      </mat-dialog-content>
      
      <mat-dialog-actions align="end" class="dialog-actions">
        <button mat-stroked-button (click)="onCancel()" [disabled]="processing" class="cancel-button">
          <mat-icon>close</mat-icon>
          Cancelar
        </button>
        <button 
          mat-raised-button 
          color="primary" 
          (click)="onConfirm()" 
          [disabled]="!accepted || processing"
          class="confirm-button">
          <mat-icon *ngIf="!processing">edit</mat-icon>
          <mat-spinner *ngIf="processing" diameter="20" class="button-spinner"></mat-spinner>
          <span *ngIf="!processing">Confirmar y Firmar</span>
          <span *ngIf="processing">Firmando documento...</span>
        </button>
      </mat-dialog-actions>
    </div>
  `,
  styles: [`
    .dialog-container {
      padding: 0;
      min-width: 500px;
      max-width: 600px;
    }

    .dialog-header {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 24px 24px 20px 24px;
      border-bottom: 1px solid rgba(0, 0, 0, 0.12);
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;

      .header-icon {
        font-size: 32px;
        width: 32px;
        height: 32px;
        color: white;
      }

      h2 {
        margin: 0;
        font-size: 24px;
        font-weight: 600;
        color: white;
        flex: 1;
      }
    }

    .dialog-content {
      padding: 24px;
    }

    .info-section {
      display: flex;
      align-items: flex-start;
      gap: 16px;
      margin-bottom: 24px;
      padding: 16px;
      background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
      border-radius: 8px;
      border-left: 4px solid #2196f3;
      box-shadow: 0 2px 4px rgba(33, 150, 243, 0.1);

      .info-icon {
        color: #1976d2;
        font-size: 24px;
        width: 24px;
        height: 24px;
        margin-top: 2px;
        flex-shrink: 0;
      }

      .info-text {
        margin: 0;
        color: #1565c0;
        line-height: 1.6;
        font-size: 14px;
        flex: 1;

        strong {
          color: #0d47a1;
          font-weight: 600;
        }
      }
    }

    .details-section {
      margin-bottom: 24px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .detail-item {
      display: flex;
      align-items: flex-start;
      gap: 16px;
      padding: 16px;
      background-color: #f5f5f5;
      border-radius: 8px;
      border: 1px solid rgba(0, 0, 0, 0.08);
      transition: all 0.2s ease;

      &:hover {
        background-color: #eeeeee;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
      }

      .detail-icon {
        color: #757575;
        font-size: 24px;
        width: 24px;
        height: 24px;
        margin-top: 2px;
        flex-shrink: 0;
      }

      .detail-content {
        display: flex;
        flex-direction: column;
        gap: 4px;
        flex: 1;
      }

      .detail-label {
        font-size: 12px;
        font-weight: 600;
        color: #9e9e9e;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }

      .detail-value {
        font-size: 14px;
        color: #212121;
        line-height: 1.5;
        word-break: break-word;
      }

      .detail-email {
        display: block;
        font-size: 13px;
        color: #757575;
        margin-top: 4px;
      }
    }

    .acceptance-section {
      padding: 20px;
      background-color: #fafafa;
      border-radius: 8px;
      border: 2px solid #e0e0e0;
      transition: all 0.2s ease;
    }

    .acceptance-section.accepted {
      background-color: #e8f5e9;
      border-color: #4caf50;
    }

    .accept-checkbox {
      display: flex;
      align-items: center;
      margin: 0;
      font-size: 14px;
      color: #424242;
      line-height: 1.5;

      ::ng-deep .mdc-checkbox {
        margin-right: 12px;
      }
    }

    .dialog-actions {
      display: flex;
      justify-content: flex-end;
      gap: 12px;
      padding: 16px 24px 24px 24px;
      border-top: 1px solid rgba(0, 0, 0, 0.12);
      background-color: #fafafa;

      button {
        display: flex;
        align-items: center;
        gap: 8px;
        min-width: 140px;
        justify-content: center;
        padding: 8px 24px;
        font-size: 14px;
        font-weight: 500;
        text-transform: none;
        border-radius: 4px;

        mat-icon {
          font-size: 20px;
          width: 20px;
          height: 20px;
        }
      }

      .cancel-button {
        color: #757575;
        border-color: rgba(0, 0, 0, 0.12);

        &:hover:not(:disabled) {
          background-color: #f5f5f5;
        }
      }

      .confirm-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;

        &:hover:not(:disabled) {
          opacity: 0.9;
          box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
        }

        &:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
      }

      .button-spinner {
        display: inline-block;
        margin: 0;
      }
    }

    ::ng-deep {
      .mat-mdc-dialog-container {
        padding: 0 !important;
        overflow: hidden;
      }

      .mat-mdc-dialog-content {
        padding: 0 !important;
        margin: 0 !important;
        max-height: none !important;
      }
    }
  `]
})
export class SignDialogComponent {
  accepted = false;
  processing = false;

  constructor(
    public dialogRef: MatDialogRef<SignDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: SignDialogData
  ) {}

  onCancel(): void {
    this.dialogRef.close(false);
  }

  onConfirm(): void {
    if (this.accepted) {
      this.processing = true;
      this.dialogRef.close(true);
    }
  }
}

