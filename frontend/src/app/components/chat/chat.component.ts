import { Component, OnInit, OnDestroy, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ChatService, Message } from '../../services/chat.service';
import { AuthService } from '../../services/auth.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatDialog } from '@angular/material/dialog';
import { Subscription } from 'rxjs';
import { FinalizeChatDialogComponent } from './finalize-chat-dialog.component';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss']
})
export class ChatComponent implements OnInit, OnDestroy, AfterViewChecked {
  @ViewChild('messagesContainer') private messagesContainer!: ElementRef;
  
  chatForm: FormGroup;
  messages: Message[] = [];
  loading = false;
  status: any = null;
  private messagesSubscription?: Subscription;
  private shouldScroll = false;

  constructor(
    private fb: FormBuilder,
    private chatService: ChatService,
    private authService: AuthService,
    private snackBar: MatSnackBar,
    private dialog: MatDialog
  ) {
    this.chatForm = this.fb.group({
      message: ['', [Validators.required, Validators.maxLength(1000)]]
    });
  }

  ngOnInit(): void {
    this.loadStatus();
    this.subscribeToMessages();
    // Siempre cargar mensajes cuando se inicializa el componente
    this.loadMessages();
  }

  ngAfterViewChecked(): void {
    if (this.shouldScroll) {
      this.scrollToBottom();
      this.shouldScroll = false;
    }
  }

  ngOnDestroy(): void {
    if (this.messagesSubscription) {
      this.messagesSubscription.unsubscribe();
    }
  }

  loadStatus(): void {
    this.chatService.getStatus().subscribe({
      next: (status) => {
        this.status = status;
      },
      error: (error) => {
        console.error('Error loading status:', error);
      }
    });
  }

  loadMessages(): void {
    // Cargar mensajes del servidor y actualizar el BehaviorSubject del servicio
    // La suscripción a messages$ se encargará de actualizar la vista automáticamente
    this.chatService.loadAndUpdateMessages();
  }

  subscribeToMessages(): void {
    // Suscribirse a los mensajes del servicio (BehaviorSubject)
    this.messagesSubscription = this.chatService.messages$.subscribe(messages => {
      this.messages = messages;
      this.shouldScroll = true;
    });
  }

  sendMessage(): void {
    if (this.chatForm.valid && !this.loading) {
      const messageText = this.chatForm.get('message')?.value;
      if (!messageText.trim()) return;

      this.loading = true;
      // Obtener nombre y email para consistencia
      // Priorizar nombre sobre email para mejor experiencia
      const username = this.authService.getUsername() || this.authService.getEmail() || 'Usuario';
      const userEmail = this.authService.getEmail();
      
      // Usar nombre si está disponible, si no usar email
      const senderName = username;

      // Agregar mensaje localmente inmediatamente
      // El servidor determinará el sender final (puede incluir email para reconocimiento)
      const newMessage: Message = {
        id: Date.now().toString(),
        content: messageText,
        sender: senderName, // El servidor puede modificarlo para incluir email
        timestamp: new Date().toISOString()
      };
      this.chatService.addMessage(newMessage);

      // Enviar al servidor
      this.chatService.sendMessage(messageText).subscribe({
        next: (response) => {
          this.loading = false;
          this.chatForm.reset();
          this.snackBar.open('Mensaje enviado y cifrado correctamente', 'Cerrar', {
            duration: 2500,
            panelClass: ['success-snackbar'],
            verticalPosition: 'top',
            horizontalPosition: 'end'
          });
        },
        error: (error) => {
          this.loading = false;
          const errorMessage = error?.error?.detail || error?.message || 'Error de conexión';
          this.snackBar.open(`No se pudo enviar el mensaje: ${errorMessage}`, 'Cerrar', {
            duration: 4000,
            panelClass: ['error-snackbar'],
            verticalPosition: 'top',
            horizontalPosition: 'end'
          });
        }
      });
    }
  }

  onKeyPress(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  formatTimestamp(timestamp: string): string {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('es-ES', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  }

  isOwnMessage(message: Message): boolean {
    // Verificar si el mensaje es propio comparando solo por nombre
    // El sender siempre será solo el nombre (sin email)
    const currentUsername = this.authService.getUsername();
    
    if (!message.sender || !currentUsername) {
      return false;
    }
    
    // Comparar directamente el nombre del sender con el nombre actual
    return message.sender === currentUsername;
  }

  isAdmin(): boolean {
    return this.authService.isAdmin();
  }

  finalizeChat(): void {
    if (!this.isAdmin()) {
      return;
    }

    const dialogRef = this.dialog.open(FinalizeChatDialogComponent, {
      width: '450px',
      disableClose: true,
      panelClass: 'finalize-chat-dialog'
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loading = true;
        this.chatService.clearChatHistory().subscribe({
          next: (response) => {
            this.loading = false;
            // Limpiar mensajes localmente
            this.chatService.clearMessages();
            this.messages = [];
            
            const messageCount = response.count || 0;
            this.snackBar.open(`Chat finalizado. ${messageCount} mensaje${messageCount !== 1 ? 's' : ''} eliminado${messageCount !== 1 ? 's' : ''}.`, 'Cerrar', {
              duration: 4000,
              panelClass: ['success-snackbar'],
              verticalPosition: 'top',
              horizontalPosition: 'end'
            });
          },
          error: (error) => {
            this.loading = false;
            const errorMessage = error?.error?.detail || error?.message || 'Error al finalizar el chat';
            this.snackBar.open(`Error: ${errorMessage}`, 'Cerrar', {
              duration: 4000,
              panelClass: ['error-snackbar'],
              verticalPosition: 'top',
              horizontalPosition: 'end'
            });
          }
        });
      }
    });
  }

  private scrollToBottom(): void {
    try {
      const element = this.messagesContainer.nativeElement;
      element.scrollTop = element.scrollHeight;
    } catch (err) {
      console.error('Error scrolling:', err);
    }
  }
}

