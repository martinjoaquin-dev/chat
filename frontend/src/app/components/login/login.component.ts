import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {
  loginForm: FormGroup;
  loading = false;
  hidePassword = true;

  // Credenciales de prueba para mostrar
  testCredentials = [
    { username: 'admin', password: 'admin123' },
    { username: 'usuario1', password: 'password1' },
    { username: 'test', password: 'test123' },
    { username: 'demo', password: 'demo123' }
  ];

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router,
    private snackBar: MatSnackBar
  ) {
    this.loginForm = this.fb.group({
      username: ['', [Validators.required]],
      password: ['', [Validators.required]]
    });
  }

  ngOnInit(): void {
    // Si ya está autenticado, redirigir al dashboard
    if (this.authService.isAuthenticated()) {
      this.router.navigate(['/']);
    }
  }

  onSubmit(): void {
    if (this.loginForm.valid) {
      this.loading = true;
      const { username, password } = this.loginForm.value;

      this.authService.login(username, password).subscribe({
        next: (response) => {
          if (response.success) {
            this.snackBar.open(`¡Bienvenido, ${response.username || username}!`, 'Cerrar', {
              duration: 3000,
              panelClass: ['success-snackbar'],
              verticalPosition: 'top',
              horizontalPosition: 'end'
            });
            this.router.navigate(['/']);
          } else {
            this.showError('Credenciales inválidas');
          }
          this.loading = false;
        },
        error: (error) => {
          this.showError('Error al iniciar sesión. Verifica tus credenciales.');
          this.loading = false;
        }
      });
    } else {
      this.showError('Por favor completa todos los campos');
    }
  }

  private showError(message: string): void {
    this.snackBar.open(message, 'Cerrar', {
      duration: 5000,
      panelClass: ['error-snackbar'],
      verticalPosition: 'top',
      horizontalPosition: 'end'
    });
  }

  fillCredentials(username: string, password: string): void {
    this.loginForm.patchValue({ username, password });
  }

  loginWithGoogle(): void {
    this.loading = true;
    this.authService.loginWithGoogle().subscribe({
      next: () => {
        // La redirección se maneja automáticamente en el servicio
      },
      error: (error) => {
        this.showError('Error al iniciar sesión con Google. Por favor, intenta nuevamente.');
        this.loading = false;
      }
    });
  }
}

