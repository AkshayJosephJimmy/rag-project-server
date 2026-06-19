
from fastapi import APIRouter,HTTPException,Depends

from database import supabase
from auth import get_current_user_id
from pydantic import BaseModel
from typing import Optional



router=APIRouter(
    tags=["chats"]
)
class ChatModel(BaseModel):
    title:str
    project_id:str


@router.post("/api/chats")
async def create_chat(chat:ChatModel,clerk_id :str=Depends(get_current_user_id)):


    try:
        result =supabase.table("chats").insert({
            "title": chat.title,
            "project_id": chat.project_id,
            "clerk_id": clerk_id
        }).execute()

        return {"message": "Chat created successfully",
                "data": result.data[0]}

    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "Error occurred while creating chat", "error": str(e)})
    




@router.delete("/api/chats/{chat_id}")

async def delete_chat(chat_id:str,clerk_id :str=Depends(get_current_user_id)):

    try:
        deletedChat = supabase.table("chats").delete().eq("id",chat_id).eq("clerk_id", clerk_id).execute()

        if not deletedChat.data:
            raise HTTPException(status_code=404, detail="Chat not found or access denied")

        return {"message": "Chat deleted successfully",
                "data": deletedChat.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "Error occurred while deleting chat", "error": str(e)})
    

















