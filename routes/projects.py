from fastapi import APIRouter,HTTPException,Depends
from database import supabase
from auth import get_current_user_id
from pydantic import BaseModel
from typing import Optional


class ProjectModel(BaseModel):
    name:str
    description:str=""


class ProjectSettingsModel(BaseModel):
    embedding_model: str
    rag_strategy: str
    agent_type: str
    chunks_per_search: int
    final_context_size: int
    similarity_threshold: float
    number_of_queries: int
    reranking_enabled: bool
    reranking_model: str
    vector_weight: float
    keyword_weight: float


router=APIRouter(
    tags=["projects"]
)

@router.get("/api/projects")

def get_projects(clerk_id :str =Depends(get_current_user_id)):

    try:
        result=supabase.table("projects").select("*").eq("clerk_id",clerk_id).execute()

        return {"message": "Projects retrieved successfully",
                "data": result.data}

    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "Error occurred while retrieving projects", "error": str(e)})
    



@router.post("/api/projects")
def create_project(project:ProjectModel,clerk_id :str =Depends(get_current_user_id)):
    try:
        #create new project in database
        project_result=supabase.table("projects").insert({
            "name": project.name,
            "description": project.description,
            "clerk_id": clerk_id
        }).execute()

        if not project_result.data:
            raise HTTPException(status_code=500, detail="Failed to create project")
        
        #create default project settings
        created_project=project_result.data[0]
        project_id=created_project.get("id")
        project_setting=supabase.table("project_settings").insert({
            "project_id": project_id,
            "embedding_model": "text-embedding-3-large",
            "rag_strategy": "basic",
            "agent_type": "agentic",
            "chunks_per_search": 10,
            "final_context_size": 5,
            "similarity_threshold": 0.3,
            "number_of_queries": 5,
            "reranking_enabled": True,
            "reranking_model": "reranker-english-v3.0",
            "vector_weight": 0.7,
            "keyword_weight": 0.3

        }).execute()

        if not project_setting.data:
            supabase.table("projects").delete().eq("id", project_id).execute()  # Rollback project creation
            raise HTTPException(status_code=500, detail="Failed to create project settings")
        
        return {"message": "Project created successfully",
                "data": created_project}



    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "Error occurred while creating project", "error": str(e)})
    


@router.delete("/api/projects/{project_id}")
def delete_project(project_id:str,clerk_id :str =Depends(get_current_user_id)):

    try:

        project_result=supabase.table("projects").select("*").eq("clerk_id",clerk_id).execute()

        if not project_result.data:
            raise HTTPException(status_code=404, detail="Project not found or access denied")
        
        deleted_project=supabase.table("projects").delete().eq("id", project_id).eq("clerk_id", clerk_id).execute()
        if not deleted_project.data:
            raise HTTPException(status_code=500, detail="failed to delete project")
        

        return {"message": "Project deleted successfully",
                "data": deleted_project.data[0]}
    
    
       
        


    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "Error occurred while deleting project", "error": str(e)})
    


@router.get("/api/projects/{project_id}")
async def get_project(project_id:str,clerk_id :str=Depends(get_current_user_id)):

    try:
        result=supabase.table("projects").select("*").eq("id",project_id).eq("clerk_id",clerk_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Project not found or access denied")

        return {"message": "Project retrieved successfully",
                "data": result.data[0] }
        


    

    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "Error occurred while retrieving project", "error": str(e)})
    


@router.get("/api/projects/{project_id}/chats")

def get_chats(project_id:str,clerk_id :str=Depends(get_current_user_id)):

    try:
        #check if project exists and belongs to user
        
        
        chats_result=supabase.table("chats").select("*").eq("project_id",project_id).order("created_at", desc=True).eq("clerk_id", clerk_id).execute()

        return {"message": "Chats retrieved successfully",
                "data": chats_result.data}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "Error occurred while retrieving chats", "error": str(e)})
    


@router.get("/api/projects/{project_id}/settings")
def get_project_settings(project_id:str,clerk_id:str=Depends(get_current_user_id)):

    try:
        settings_result=supabase.table("project_settings").select("*").eq("project_id",project_id).execute()

        if not settings_result.data:
            raise HTTPException(status_code=404, detail="Project settings not found")
        
        return {"message": "Project settings retrieved successfully",
                "data": settings_result.data[0]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "Error occurred while retrieving project settings", "error": str(e)})


@router.get("/api/projects/{project_id}/documents")

def get_project_documents(project_id:str,clerk_id :str=Depends(get_current_user_id)):

    try:
        documents_result=supabase.table("project_documents").select("*").eq("project_id",project_id).eq("clerk_id", clerk_id).execute()
        if not documents_result.data:
            raise HTTPException(status_code=404, detail="No documents found for this project or access denied")

        return {"message": "Project documents retrieved successfully",
                "data": documents_result.data}
    

    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "Error occurred while retrieving project documents", "error": str(e)})
    


@router.put("/api/projects/{project_id}/settings")
def update_project_settingd(project_id:str,settings:ProjectSettingsModel,clerk_id:str=Depends(get_current_user_id)):

    try:
        
        #first we have to check if the project exists

        user=supabase.table("projects").select("id").eq("id",project_id).eq("clerk_id",clerk_id).execute()

        if not user.data:
            raise HTTPException(status_code=404, detail="Project not found or access denied")
        

        updated_settings=supabase.table("project_settings").update(settings.model_dump()).eq("project_id", project_id).execute()

        if not updated_settings.data:
            raise HTTPException(status_code=404, detail="Project settings not found")
        

        return {"message": "Project settings updated successfully",
                "data": updated_settings.data[0]}
    

    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "Error occurred while updating project settings", "error": str(e)})
        

    






        


        













