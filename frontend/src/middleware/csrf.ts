import csurf from 'csurf';
import cookieParser from 'cookie-parser';

export const csrfProtection = csurf({ cookie: true });
