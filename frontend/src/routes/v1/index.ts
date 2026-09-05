import { Router } from 'express';
import { analyticsRouter } from './analytics';
import authRouter from './auth';
import userRouter from './user';
import featureRouter from './feature';
import i18nRouter from './i18n';
import { webhooksRouter } from './webhooks';
import docsRouter from './docs';
import { healthRouter } from './health';

export const apiV1Router = Router();

apiV1Router.use('/analytics', analyticsRouter);
apiV1Router.use('/auth', authRouter);
apiV1Router.use('/user', userRouter);
apiV1Router.use('/feature', featureRouter);
apiV1Router.use('/i18n', i18nRouter);
apiV1Router.use('/webhooks', webhooksRouter);
apiV1Router.use('/docs', docsRouter);
apiV1Router.use('/health', healthRouter);
