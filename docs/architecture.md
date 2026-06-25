# Workflow Engine Architecture

## Overview

This service uses FastAPI for APIs, SQLAlchemy for persistence, PostgreSQL for storage, Redis and Celery for asynchronous execution, and JWT for authentication.

## Flow

1. Authenticated users create workflow definitions.
2. Users start executions through the API.
3. Execution jobs are queued to Celery.
4. Workers process steps and persist logs.
5. Dashboard endpoints summarize execution metrics.
