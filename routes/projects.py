from fastapi import APIRouter,HTTPException,Depends
from database import supabase
 



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




