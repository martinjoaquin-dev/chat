import { Component } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-finalize-chat-dialog',
  template: `
    <div class="dialog-container">
      <div class="dialog-header">
        <mat-icon class="warning-icon">warning</mat-icon>
        <h2>Finalizar Chat</h2>
      </div>
      
      <div class="dialog-content">
        <p>¿Estás seguro de que deseas finalizar el chat?</p>
        <p class="warning-text">Esto eliminará todo el historial de mensajes de forma permanente.</p>
      </div>
      
      <div class="dialog-actions">
        <button mat-stroked-button (click)="cancel()" class="cancel-button">
          <mat-icon>close</mat-icon>
          Cancelar
        </button>
        <button mat-raised-button color="warn" (click)="confirm()" class="confirm-button">
          <mat-icon>delete_sweep</mat-icon>
          Finalizar Chat
        </button>
      </div>
    </div>
  `,
  styles: [`
    .dialog-container {
      padding: 0;
      min-width: 400px;
    }

    .dialog-header {
      display: flex;
      align-items: center;
      gap: var(--spacing-md);
      padding: var(--spacing-lg);
      border-bottom: 1px solid var(--border-color);
      background: var(--surface-elevated);

      .warning-icon {
        color: #f59e0b;
        font-size: 32px;
        width: 32px;
        height: 32px;
      }

      h2 {
        margin: 0;
        font-size: var(--font-size-xl);
        font-weight: 600;
        color: var(--text-primary);
      }
    }

    .dialog-content {
      padding: var(--spacing-lg);
      color: var(--text-primary);

      p {
        margin: 0 0 var(--spacing-md) 0;
        font-size: var(--font-size-base);
        line-height: 1.6;

        &:last-child {
          margin-bottom: 0;
        }
      }

      .warning-text {
        color: #f59e0b;
        font-weight: 500;
      }
    }

    .dialog-actions {
      display: flex;
      justify-content: flex-end;
      gap: var(--spacing-md);
      padding: var(--spacing-md) var(--spacing-lg);
      border-top: 1px solid var(--border-color);
      background: var(--surface);

      button {
        display: flex;
        align-items: center;
        gap: var(--spacing-xs);
        min-width: 120px;
      }

      .cancel-button {
        color: var(--text-secondary);
      }

      .confirm-button {
        background: #ef4444;
        color: white;

        &:hover {
          background: #dc2626;
        }
      }
    }
  `]
})
export class FinalizeChatDialogComponent {
  constructor(
    public dialogRef: MatDialogRef<FinalizeChatDialogComponent>
  ) {}

  cancel(): void {
    this.dialogRef.close(false);
  }

  confirm(): void {
    this.dialogRef.close(true);
  }
}

