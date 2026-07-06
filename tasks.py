from celery import Celery
from database import supabase
import time
from database import s3_client,BUCKET_NAME
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.docx import partition_docx
from unstructured.partition.html import partition_html

celery_app =Celery(
    "document_processor",#name of the celery app
    broker="redis://localhost:6379/0",#where tasks are queued
    backend="redis://localhost:6379/0" #where results are stored
)

def update_status(document_id:str,status:str,details:dict=None):


    """update the status of the document in the database"""

    #update the status of the docuemnt

    result=supabase.table("project_documents").select("processing_details").eq("id", document_id).execute()
    current_details={}


    if result.data and result.data[0]["processing_details"]:
        current_details=result.data[0]["processing_details"]

    if details:
       current_details.update(details)

      



    
    supabase.table("project_documents").update({"processing_status": status, "processing_details": current_details}).eq("id", document_id).execute()


@celery_app.task
def process_document(document_id:str):

  try:
    
    doc_result=supabase.table("project_documents").select("*").eq("id", document_id).execute()

    document=doc_result.data[0]


    update_status(document_id,"processing")


    #1.download the document from s3 or url based on the source_type

    elements=downlaod_and_partition(document_id,document)
    table=sum(1 for e in elements if e.category=="Table")
    image=sum(1 for e in elements if e.category=="Image")
    text_element=sum(1 for e in elements if e.category in ["NarrativeText","Title","Text"])
    print(f"Document {document_id} partitioned into {len(elements)} elements: {table} tables, {image} images, and {text_element} text elements.")

   


    #2.chunk elements

    #3.summarize chunk

    #4.vectorization and storing


    return{"status": "success", "message": f"Document {document_id} processed successfully."}


  except Exception as e:
    return{"status": "error", "message": f"Error processing document {document_id}: {str(e)}"} 


   

def downlaod_and_partition(document_id:str,document:dict):

    s3_key=document["s3_key"]

    source_type=document.get("source_type","file")

    if source_type=="url":
       pass
    else:

     filename=document["filename"]
     file_type=filename.split(".")[-1]
     file_size=document["file_size"]




     temp_file_path=f"/tmp/temp_{document_id}.{file_type}"
     s3_client.download_file(BUCKET_NAME,s3_key,temp_file_path)
     

     elements=partition_document(temp_file_path,file_type,source_type)
     elements_found=analyze_elements(elements)


    update_status(document_id,"chunking",{"partitioning":{
       "elements_summary":
        elements_found

    }}) 


   
    return elements



def partition_document(temp_path:str,file_type:str,source_type:str="file"):

     """partition the document based on the file type and source type and return the elements"""


     if source_type=="url":
        pass
     else:
        if file_type=="pdf":
            elements=partition_pdf( filename=temp_path,                  # mandatory
                                    strategy="hi_res",                                     # mandatory to use ``hi_res`` strategy
                                    infer_table_structure=True,                               # optional
                                    extract_images_in_pdf=True,                            # mandatory to set as ``True``
                                    extract_image_block_types=["Image"],          # optional
                                    extract_image_block_to_payload=True,                  # optional
                                    )
        elif file_type=="docx":
            elements=partition_docx(temp_path)
        elif file_type=="html":
            elements=partition_html(temp_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

     return elements
  

def analyze_elements(elements:list):
   
   table_count=0
   image_count=0
   text_count=0
   title_count=0
   other_count=0

   for element in elements:
      element_name=type(element).__name__
      if element_name=="Table":
         table_count+=1
      elif element_name=="Image":
         image_count+=1
      elif element_name in ["NarrativeText","Text"]:
         text_count+=1
      elif element_name in ["Title","Header"]:
         title_count+=1
      else:
         other_count+=1


   return {
        "tables": table_count,
        "images": image_count,
        "text": text_count,
        "titles": title_count,
        "other": other_count
     } 







