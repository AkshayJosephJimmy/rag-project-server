import uuid

from fastapi import APIRouter,HTTPException,Depends
from database import supabase,s3_client,BUCKET_NAME
from auth import get_current_user_id
from pydantic import BaseModel
from typing import Optional



router=APIRouter(
    tags=["files"])


class fileLoadRequest(BaseModel):
    filename:str
    file_type:str
    file_size:int


@router.get("/api/projects/{project_id}/files")

def get_project_documents(project_id:str,clerk_id :str=Depends(get_current_user_id)):

    try:
        documents_result=supabase.table("project_documents").select("*").eq("project_id",project_id).eq("clerk_id", clerk_id).execute()
        

        return {"message": "Project documents retrieved successfully",
                "data": documents_result.data or []}  # Return an empty list if data is None
    

    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "Error occurred while retrieving project files", "error": str(e)})
    



@router.post("/api/projects/{project_id}/files/upload-file")
def upload_file(file_request:fileLoadRequest,project_id:str,clerk_id:str=Depends(get_current_user_id)):

    try:

        #verify prjoject and user exists

        project_exists=supabase.table('projects').select('id').eq('id',project_id).eq('clerk_id', clerk_id).execute()
        if not project_exists.data:
            raise HTTPException(status_code=404, detail="Project not found or access denied")


        #generate s3 key

        unique_id=str(uuid.uuid4())
        s3_key=f"{clerk_id}/{project_id}/{unique_id}_{file_request.filename}"





        #create presigned url
        presigned_url=s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': s3_key,
                'ContentType': file_request.file_type
                
            },
            ExpiresIn=3600
            )
        
        #create database record 
        document_result=supabase.table("project_documents").insert({
            "project_id": project_id,
            "clerk_id": clerk_id,
            "processing_status": "uploading",
            "filename": file_request.filename,
            "file_type": file_request.file_type,
            "file_size": file_request.file_size,
            "s3_key": s3_key
        }).execute()

        if not document_result.data:
            raise HTTPException(status_code=500, detail="Failed to create document record")
        

        return {"message": "Presigned URL generated successfully",
                "data": {
                    "presigned_url": presigned_url,
                    "s3_key": s3_key,
                    "document":document_result.data[0]
                }}


        

    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "Error occurred while generating upload URL", "error": str(e)})
    


@router.post("/api/projects/{project_id}/files/confirm")
def confirm_file_upload(confirm_req:dict,project_id:str,clerk_id:str=Depends(get_current_user_id)):

    try:
        s3_key=confirm_req.get("s3_key")
        if not s3_key:
            raise HTTPException(status_code=400, detail="s3_key is required")
        
        #verify the document record exists and belongs to the user and project
        document_result=supabase.table("project_documents").select("*").eq("project_id", project_id).eq("clerk_id", clerk_id).eq("s3_key", s3_key).execute()

        if not document_result.data:
            raise HTTPException(status_code=404, detail="Document not found or access denied")
        
        #update processing status to uploaded
        supabase.table("project_documents").update({"processing_status": "queued"}).eq("project_id", project_id).eq("clerk_id", clerk_id).eq("s3_key", s3_key).execute()

        #proccessing starts


        return {"message": "File upload confirmed successfully,processing started with celery",
                "data": document_result.data[0],"processing_status": "queued"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "Error occurred while confirming file upload", "error": str(e)})


class UrlAddRequest(BaseModel):
    url:str
    

@router.post("/api/projects/{project_id}/urls")
def add_url(
    project_id:str,
    url_request:UrlAddRequest,
    clerk_id:str=Depends(get_current_user_id)
):
    
    try:
        url=url_request.url.strip()

        if not url.startswith(('http://','https://')):
            url='https://'+url


        document_result=supabase.table("project_documents").insert({
            "project_id": project_id,
            "clerk_id": clerk_id,
            "processing_status": "queued",
            "filename": url_request.url,
            "file_type": "url",
            "file_size": 0,
            "s3_key": '',
            "source_url": url,
            "source_type": "url"
        }).execute()

        if not document_result.data:
            raise HTTPException(status_code=500, detail="Failed to create document record")
        
        return {"message": "URL added successfully",
                "data": document_result.data[0]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "Error occurred while adding URL", "error": str(e)})


        
    

