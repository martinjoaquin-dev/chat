import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError, BehaviorSubject } from 'rxjs';
import { catchError, filter, take, switchMap } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  private isRefreshing = false;
  private refreshTokenSubject: BehaviorSubject<any> = new BehaviorSubject<any>(null);

  constructor(private authService: AuthService) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Obtener token (puede ser de autenticación tradicional o OAuth)
    const token = this.authService.getToken();
    
    // Agregar token al header si existe
    if (token) {
      req = req.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`
        }
      });
    }
    
    // Manejar la respuesta
    return next.handle(req).pipe(
      catchError((error: HttpErrorResponse) => {
        // Si el error es 401 (Unauthorized), intentar refrescar el token
        if (error.status === 401 && token && this.authService.isOAuthAuthenticated()) {
          return this.handle401Error(req, next);
        }
        
        // Si no es 401 o no hay refresh token, lanzar el error
        return throwError(() => error);
      })
    );
  }

  private handle401Error(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    if (!this.isRefreshing) {
      this.isRefreshing = true;
      this.refreshTokenSubject.next(null);

      // Intentar refrescar el token
      return this.authService.refreshAccessToken().pipe(
        switchMap((tokens: any) => {
          this.isRefreshing = false;
          this.refreshTokenSubject.next(tokens.access_token);
          
          // Reintentar la petición original con el nuevo token
          return next.handle(this.addTokenHeader(req, tokens.access_token));
        }),
        catchError((error) => {
          this.isRefreshing = false;
          
          // Si el refresh falla, hacer logout
          this.authService.logout();
          return throwError(() => error);
        })
      );
    }

    // Si ya está refrescando, esperar a que termine
    return this.refreshTokenSubject.pipe(
      filter(token => token !== null),
      take(1),
      switchMap((token) => next.handle(this.addTokenHeader(req, token)))
    );
  }

  private addTokenHeader(req: HttpRequest<any>, token: string): HttpRequest<any> {
    return req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
  }
}

