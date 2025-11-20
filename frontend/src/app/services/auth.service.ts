import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject, tap, from, of } from 'rxjs';
import { Router } from '@angular/router';

export interface LoginResponse {
  success: boolean;
  token?: string;
  username?: string;
  message?: string;
}

export interface OAuthTokens {
  access_token: string;
  id_token?: string;
  refresh_token?: string;
  expires_in?: number;
  scope?: string;
}

export interface GoogleLoginResponse {
  authorization_url: string;
  state: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://localhost:8000/api';
  private tokenKey = 'auth_token';
  private idTokenKey = 'oauth_id_token';
  private refreshTokenKey = 'oauth_refresh_token';
  private usernameKey = 'username';
  private emailKey = 'oauth_email';
  private userInfoKey = 'oauth_user_info';
  
  private isAuthenticatedSubject = new BehaviorSubject<boolean>(this.hasToken());
  public isAuthenticated$ = this.isAuthenticatedSubject.asObservable();

  constructor(
    private http: HttpClient,
    private router: Router
  ) {}

  login(username: string, password: string): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.apiUrl}/auth/login`, {
      username,
      password
    }).pipe(
      tap(response => {
        if (response.success && response.token) {
          this.setToken(response.token);
          if (response.username) {
            localStorage.setItem(this.usernameKey, response.username);
          }
          this.isAuthenticatedSubject.next(true);
        }
      })
    );
  }

  getToken(): string | null {
    // Intentar obtener token OAuth primero (id_token o access_token)
    const idToken = localStorage.getItem(this.idTokenKey);
    if (idToken) {
      return idToken;
    }
    
    const accessToken = localStorage.getItem(this.tokenKey);
    // Verificar si es un token OAuth (access_token puede estar guardado también)
    if (accessToken && accessToken.length > 100) { // Los tokens OAuth son más largos
      // Verificar si tenemos email OAuth guardado (indicador de OAuth)
      const oauthEmail = localStorage.getItem(this.emailKey);
      if (oauthEmail) {
        return accessToken; // Es un access_token de OAuth
      }
    }
    
    // Si no hay OAuth, usar token tradicional
    return accessToken;
  }

  getUsername(): string | null {
    return localStorage.getItem(this.usernameKey);
  }

  private setToken(token: string): void {
    localStorage.setItem(this.tokenKey, token);
  }

  private hasToken(): boolean {
    return !!this.getToken();
  }

  isAuthenticated(): boolean {
    return this.hasToken();
  }

  getCurrentUser(): Observable<any> {
    return this.http.get(`${this.apiUrl}/auth/me`);
  }

  isAdmin(): boolean {
    const username = this.getUsername();
    const email = this.getEmail();
    
    // Verificar por username (autenticación tradicional)
    if (username && username.toLowerCase() === 'admin') {
      return true;
    }
    
    // Verificar por email (OAuth)
    if (email && email.toLowerCase().includes('admin')) {
      return true;
    }
    
    return false;
  }

  /**
   * Inicia el flujo OAuth 2.0 con Google usando Authorization Code + PKCE.
   */
  loginWithGoogle(): Observable<GoogleLoginResponse> {
    return this.http.get<GoogleLoginResponse>(`${this.apiUrl}/auth/google/login`).pipe(
      tap(response => {
        // Redirigir al usuario a Google para autenticación
        if (response.authorization_url) {
          window.location.href = response.authorization_url;
        }
      })
    );
  }

  /**
   * Maneja el callback de OAuth y almacena los tokens.
   */
  async handleOAuthCallback(tokens: OAuthTokens): Promise<void> {
    try {
      // Almacenar tokens
      if (tokens.access_token) {
        localStorage.setItem(this.tokenKey, tokens.access_token);
      }
      
      if (tokens.id_token) {
        localStorage.setItem(this.idTokenKey, tokens.id_token);
        // Decodificar id_token para obtener información del usuario
        const userInfo = this.decodeIdToken(tokens.id_token);
        if (userInfo) {
          localStorage.setItem(this.emailKey, userInfo.email || '');
          localStorage.setItem(this.userInfoKey, JSON.stringify(userInfo));
          // PRIORIZAR nombre sobre email: siempre guardar el nombre si está disponible
          if (userInfo.name) {
            localStorage.setItem(this.usernameKey, userInfo.name);
          } else if (userInfo.email) {
            // Si no hay nombre, usar el email como nombre temporal
            localStorage.setItem(this.usernameKey, userInfo.email);
          }
        }
      }
      
      if (tokens.refresh_token) {
        localStorage.setItem(this.refreshTokenKey, tokens.refresh_token);
      }
      
      // Actualizar estado de autenticación
      this.isAuthenticatedSubject.next(true);
    } catch (error) {
      console.error('Error al manejar callback OAuth:', error);
      throw error;
    }
  }

  /**
   * Decodifica un id_token JWT (sin verificar, solo para extraer información).
   */
  private decodeIdToken(idToken: string): any {
    try {
      const base64Url = idToken.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );
      return JSON.parse(jsonPayload);
    } catch (error) {
      console.error('Error al decodificar id_token:', error);
      return null;
    }
  }

  /**
   * Obtiene el email del usuario autenticado (OAuth).
   */
  getEmail(): string | null {
    return localStorage.getItem(this.emailKey);
  }

  /**
   * Obtiene información completa del usuario (OAuth).
   */
  getUserInfo(): any {
    const userInfoStr = localStorage.getItem(this.userInfoKey);
    if (userInfoStr) {
      try {
        return JSON.parse(userInfoStr);
      } catch (error) {
        console.error('Error al parsear user info:', error);
        return null;
      }
    }
    return null;
  }

  /**
   * Refresca el access_token usando el refresh_token.
   */
  refreshAccessToken(): Observable<OAuthTokens> {
    const refreshToken = localStorage.getItem(this.refreshTokenKey);
    
    if (!refreshToken) {
      throw new Error('No hay refresh token disponible');
    }
    
    return this.http.post<OAuthTokens>(`${this.apiUrl}/auth/refresh`, {
      refresh_token: refreshToken
    }).pipe(
      tap(tokens => {
        // Actualizar tokens almacenados
        if (tokens.access_token) {
          localStorage.setItem(this.tokenKey, tokens.access_token);
        }
        if (tokens.id_token) {
          localStorage.setItem(this.idTokenKey, tokens.id_token);
          const userInfo = this.decodeIdToken(tokens.id_token);
          if (userInfo) {
            localStorage.setItem(this.userInfoKey, JSON.stringify(userInfo));
            if (userInfo.email) {
              localStorage.setItem(this.emailKey, userInfo.email);
            }
            // PRIORIZAR nombre sobre email: siempre guardar el nombre si está disponible
            if (userInfo.name) {
              localStorage.setItem(this.usernameKey, userInfo.name);
            } else if (userInfo.email) {
              // Si no hay nombre, usar el email como nombre temporal
              localStorage.setItem(this.usernameKey, userInfo.email);
            }
          }
        }
        if (tokens.refresh_token) {
          localStorage.setItem(this.refreshTokenKey, tokens.refresh_token);
        }
      })
    );
  }

  /**
   * Obtiene información del usuario actual desde el backend (OAuth).
   */
  getCurrentUserOAuth(): Observable<any> {
    return this.http.get(`${this.apiUrl}/auth/oauth/me`);
  }

  /**
   * Verifica si el usuario está autenticado con OAuth.
   */
  isOAuthAuthenticated(): boolean {
    return !!localStorage.getItem(this.idTokenKey) || !!localStorage.getItem(this.tokenKey);
  }

  /**
   * Logout mejorado que limpia tanto tokens tradicionales como OAuth.
   */
  logout(): void {
    // Limpiar tokens tradicionales
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.usernameKey);
    
    // Limpiar tokens OAuth
    localStorage.removeItem(this.idTokenKey);
    localStorage.removeItem(this.refreshTokenKey);
    localStorage.removeItem(this.emailKey);
    localStorage.removeItem(this.userInfoKey);
    
    // Actualizar estado
    this.isAuthenticatedSubject.next(false);
    this.router.navigate(['/login']);
  }
}

