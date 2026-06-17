import { HttpInterceptorFn, HttpRequest, HttpHandlerFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { environment } from '../../../environments/environment';

export const apiInterceptor: HttpInterceptorFn = (
  req: HttpRequest<unknown>,
  next: HttpHandlerFn
) => {
  // Only prefix relative API paths
  const isApiCall = !req.url.startsWith('http');
  const apiReq = isApiCall
    ? req.clone({
        url: `${environment.apiUrl}/${req.url}`,
        setHeaders: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
      })
    : req;

  return next(apiReq);
};
