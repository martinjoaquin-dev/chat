import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-auth-callback',
  template: `
    <div class="auth-callback-container">
      <div class="loading-spinner">
        <div *ngIf="loading" class="spinner-wrapper">
          <mat-spinner diameter="50"></mat-spinner>
        </div>
        <p>{{ message }}</p>
      </div>
    </div>
  `,
  styles: [`
    .auth-callback-container {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      background-color: #f5f5f5;
    }
    .loading-spinner {
      text-align: center;
    }
    .spinner-wrapper {
      display: flex;
      justify-content: center;
      margin-bottom: 20px;
    }
    .loading-spinner p {
      margin-top: 20px;
      font-size: 16px;
      color: #666;
    }
  `]
})
export class AuthCallbackComponent implements OnInit {
  message: string = 'Procesando autenticación...';
  loading: boolean = true;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private authService: AuthService
  ) {}

  async ngOnInit(): Promise<void> {
    // Verificar si hay error en la URL
    const error = this.route.snapshot.queryParams['error'];
    if (error) {
      this.loading = false;
      this.message = `Error de autenticación: ${error}`;
      setTimeout(() => {
        this.router.navigate(['/login']);
      }, 3000);
      return;
    }

    // Extraer tokens del fragment (más seguro que query params)
    const fragment = this.route.snapshot.fragment;
    if (fragment) {
      const params = new URLSearchParams(fragment);
      const accessToken = params.get('access_token');
      const idToken = params.get('id_token');
      const refreshToken = params.get('refresh_token');
      const expiresIn = params.get('expires_in');
      const scope = params.get('scope');

      if (accessToken) {
        try {
          // Almacenar tokens
          await this.authService.handleOAuthCallback({
            access_token: accessToken,
            id_token: idToken || undefined,
            refresh_token: refreshToken || undefined,
            expires_in: expiresIn ? parseInt(expiresIn) : undefined,
            scope: scope || undefined
          });

          this.loading = false;
          this.message = 'Autenticación exitosa. Redirigiendo...';
          setTimeout(() => {
            this.router.navigate(['/chat']);
          }, 1000);
        } catch (error: any) {
          this.loading = false;
          console.error('Error al procesar tokens OAuth:', error);
          this.message = `Error al procesar autenticación: ${error.message || 'Error desconocido'}`;
          setTimeout(() => {
            this.router.navigate(['/login']);
          }, 3000);
        }
      } else {
        this.loading = false;
        this.message = 'No se recibieron tokens de autenticación';
        setTimeout(() => {
          this.router.navigate(['/login']);
        }, 2000);
      }
    } else {
      // Si no hay fragment, verificar query params (fallback)
      const accessToken = this.route.snapshot.queryParams['access_token'];
      if (accessToken) {
        try {
          await this.authService.handleOAuthCallback({
            access_token: accessToken,
            id_token: this.route.snapshot.queryParams['id_token'] || undefined,
            refresh_token: this.route.snapshot.queryParams['refresh_token'] || undefined,
            expires_in: this.route.snapshot.queryParams['expires_in'] 
              ? parseInt(this.route.snapshot.queryParams['expires_in']) 
              : undefined
          });

          this.loading = false;
          this.message = 'Autenticación exitosa. Redirigiendo...';
          setTimeout(() => {
            this.router.navigate(['/chat']);
          }, 1000);
        } catch (error: any) {
          this.loading = false;
          console.error('Error al procesar tokens OAuth:', error);
          this.message = `Error al procesar autenticación: ${error.message || 'Error desconocido'}`;
          setTimeout(() => {
            this.router.navigate(['/login']);
          }, 3000);
        }
      } else {
        this.loading = false;
        this.message = 'No se recibieron tokens de autenticación';
        setTimeout(() => {
          this.router.navigate(['/login']);
        }, 2000);
      }
    }
  }
}
