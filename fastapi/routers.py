import os
import logging
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException, status, Depends
from models import RegisterUser, LoginUser, ExploreDocs, LoadDocument, UserPrompts

# Importing all the necessary functions
from services import          \
check_if_user_already_exists, \
register_user,                \
login_user,                   \
verify_token,                 \
explore_documents,            \
load_document,                \
download_files_from_s3,       \
generate_summary,             \
invoke_pipeline

# Setup the API router
router = APIRouter()

# Load env variables
load_dotenv()

# Logger configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Log to console (dev only)
if os.getenv('APP_ENV') == "development":
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Also log to a file
file_handler = logging.FileHandler(os.getenv('FASTAPI_LOG_FILE', "fastapi_errors.log"))
file_handler.setFormatter(formatter)
logger.addHandler(file_handler) 


# Route for FastAPI Health check
@router.get("/health")
def health() -> JSONResponse:
    ''' Check if the FastAPI application is setup and running '''

    logger.info("GET - /health request received")
    return JSONResponse({
        'status'    : status.HTTP_200_OK,
        'type'      : "string",
        'message'   : "You're viewing a page from FastAPI"
    })


# Route for registering user
@router.post("/register")
def register(user: RegisterUser):
    ''' Register new users to the application '''
    
    logger.info("FASTAPI Routers - register - Route for Registering User")
    db_user = check_if_user_already_exists(user.email)
    
    if db_user is not None:
        logger.info("FASTAPI Routers - register - User Already Exists")
        return JSONResponse({
            'status'    : status.HTTP_400_BAD_REQUEST,
            'type'      : "string",
            'message'   : "Email already registered. Please login."
        })
    
    else:
        try:
            response = register_user(user.first_name, user.last_name, user.phone, user.email, user.password)
            logger.info("FASTAPI Routers - register() - New User Registered Successfully")
            return response
        
        except Exception as e:
            logger.info(f"FASTAPI Routers - register() - Error registering user:{e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")


# Route for user login
@router.post("/login")
def login(user: LoginUser):
    ''' Sign in users to the application '''

    logger.info("FASTAPI Routers - login - Route for Logging in User")
    db_user = check_if_user_already_exists(user.email)
    
    if db_user is None:
        logger.info("FASTAPI Routers - login - User does not exist")
        return JSONResponse({
            'status'    : status.HTTP_404_NOT_FOUND,
            'type'      : "string",
            'message'   : "User not found"
        })
    
    else:
        response = login_user(db_user, user.email, user.password)
        logger.info("FASTAPI Routers - login - Login Successful")
        return response
    

# Route for Exploring Documents
@router.get("/exploredocs",
    response_class = JSONResponse,
    responses = {
        401: {'description': 'Invalid or expired token'},
        402: {'description': 'Insufficient permissions'},
        403: {'description': 'Returns a list of documents'}
    }
)
def explore_docs(
    prompt  : ExploreDocs = Depends(),
    token   : str = Depends(verify_token)
) -> JSONResponse:
    ''' Load a list of documents from the database '''
    
    logger.info("FASTAPI Routers - explore docs = Route for fetching the list of documents")
    
    # Limit the count to 10 if not specified
    if prompt.count is None:
        logger.info(f"FASTAPI Routers - explore_docs - GET - /exploredocs request received")
        prompt.count = 10
    else:
        logger.info(f"FASTAPI Routers - explore_docs - GET - /exploredocs?count={prompt.count} request received")
    
    return explore_documents(prompt.count)


# Route for Selecting a document
@router.get("/load_docs/{document_id}",
    response_class = JSONResponse,
    responses = {
        401: {'description': 'Invalid or expired token'},
        402: {'description': 'Insufficient permissions'},
        403: {'description': 'Returns all available data about a document id'}
    }
)
def load_docs(
    document_id : str,
    token       : str = Depends(verify_token)
) -> JSONResponse:
    ''' Load details about the specified document '''
    
    logger.info(f"FASTAPI Routers - load_docs = GET - /load_docs/{document_id} request received")

    logger.info(f"FASTAPI Routers - load_docs = Downloading the files present in s3 bucket - {document_id} folder")
    download_files_from_s3(document_id)
    logger.info(f"FASTAPI Routers - load_docs = Loading the entire document with id = {document_id}")
    
    return load_document(document_id)


# Route for generating summary 
@router.get("/summary/{document_id}",
    response_class = JSONResponse,
    responses = {
        401: {'description': 'Invalid or expired token'},
        402: {'description': 'Insufficient permissions'},
        403: {'description': 'Returns the summary for a document id'}
    }
)
def doc_summary(
    document_id : str,
    token       : str = Depends(verify_token)
) -> JSONResponse:
    """ Generate a summary for the specified document """
    
    logger.info(f"FASTAPI Routers - doc_summary = GET - /summary/{document_id} request received")
    return generate_summary(document_id)


# Route for RAG implementation
@router.post("/chatbot/{document_id}",
    response_class = JSONResponse,
    responses = {
        401: {'description': 'Invalid or expired token'},
        402: {'description': 'Insufficient permissions'},
        403: {'description': 'Returns a chat response for a document id'}
    }
)
def chatbot(
    prompt      : UserPrompts,
    document_id : str,
    token       : str = Depends(verify_token)
) -> JSONResponse:
    
    logger.info(f"FASTAPI Routers - chatbot = GET - /chatbot/{document_id} request received")
    
    return invoke_pipeline(document_id, prompt.question, prompt.prompt_type, prompt.source, token)