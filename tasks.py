from celery import Celery


celery_app =Celery(
    "document_processor",#name of the celery app
    broker="redis://localhost:6379/0",#where tasks are queued
    backend="redis://localhost:6379/0" #where results are stored
)