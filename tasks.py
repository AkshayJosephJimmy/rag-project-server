from celery import Celery
from database import supabase
import time

celery_app =Celery(
    "document_processor",#name of the celery app
    broker="redis://localhost:6379/0",#where tasks are queued
    backend="redis://localhost:6379/0" #where results are stored
)



@celery_app.task
def process_document(document_id:str):
    """Celery task to process a document. This is a placeholder implementation."""


    #update document status to processing
    supabase.table("project_documents").update({"processing_status": "processing"}).eq("id", document_id).execute()

    #simulate processing time
    time.sleep(5) #replace with actual processing logic

    #update document status to completed
    supabase.table("project_documents").update({"processing_status": "completed"}).eq("id", document_id).execute()

    return {"message": f"Document {document_id} processed successfully."}




