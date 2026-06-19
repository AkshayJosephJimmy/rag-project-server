from fastapi import Request,HTTPException
import os
from dotenv import load_dotenv
from clerk_backend_api  import Clerk,AuthenticateRequestOptions

load_dotenv()

sdk=Clerk(bearer_auth=os.getenv("CLERK_SECRET_KEY"))

async def get_current_user_id(request:Request)-> str:
    try:

        request_state=sdk.authenticate_request(request,AuthenticateRequestOptions(authorized_parties=["http://localhost:3000"]))
        print("Request state:", request_state)  # Debugging line to check the request state


        if not request_state.is_signed_in:
            raise HTTPException(status_code=401,detail="Unauthorized")

        client_id=request_state.payload.get("sub")

        return client_id



    except Exception as e:
        raise HTTPException(status_code=401,detail=str(e))


    
    

    



