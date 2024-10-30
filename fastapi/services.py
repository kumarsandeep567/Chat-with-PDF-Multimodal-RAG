import os
import jwt
import hmac
import boto3
import PyPDF2
import hashlib
import logging
import tiktoken
import datetime
from openai import OpenAI
from dotenv import load_dotenv
from typing import Any
from datetime import timezone, timedelta
from fastapi import status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from snowflake.connector import DictCursor
from connectDB import create_connection_to_snowflake, close_connection

# Load env variables
load_dotenv()

# Logger configuration
logging.basicConfig(level = logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("SECRET_KEY")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = 'login', auto_error = False)

# Function to hash password
def get_password_hash(password: str) -> str:
    logger.info(f"FASTAPI Services - get_password_hash() - Hashing the given password")
    hash_hex = None

    # Convert secret_key, password to bytes for hashing
     # Create HMAC hash object using secret key and password - Generate hex digest of the hash
    try:
        secret_key = SECRET_KEY.encode()
        hash_object = hmac.new(secret_key, msg=password.encode(), digestmod=hashlib.sha256)
        hash_hex = hash_object.hexdigest()
        return hash_hex
    except Exception as e:
        logger.info(f"FASTAPI Services Error - get_password_hash() - encountered an error: {e}")


# Helper function to create a JWT token with an expiration time
def create_jwt_token(data: dict) -> dict[str, Any]:
    logger.info(f"FASTAPI Services - create_jwt_token() - Create a JWT token with an expiration time")
    
    # Set token expiration time to 'x' minutes from the current time
    expiration = datetime.datetime.now(timezone.utc) + timedelta(minutes=60)
    
    # Create the token payload with expiration and provided data
    token_payload = {
        "expiration": str(expiration), 
        **data
    }
    
   # Encode the payload using the secret key and HS256 algorithm to create the token
    token = jwt.encode(token_payload, SECRET_KEY, algorithm="HS256")
    
    token_dict = {
        'token'         : token,
        'token_type'    : "Bearer"
    }
    logger.info(f"FASTAPI Services - create_jwt_token() - JWT Token created with payload")
    return token_dict


# Function to decode the JWT token and verify its validity
def decode_jwt_token(token: str):
    logger.info(f"FASTAPI Services - decode_jwt_token() - Decode JWT token & Validation")
    try:
        # Decode the JWT token
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        logger.info(f"FASTAPI Services - decode_jwt_token() - Decoded JWT token successfully")
        return decoded_token
    
    except Exception as e:
        logger.error(f"FASTAPI Services Error - decode_jwt_token() encountered an error: {e}")  
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail      = "Token expired",
            headers     = {"WWW-Authenticate": "Bearer"},
        )
    
# Helper function to check if JWT token is expired
def validate_token(token: str) -> bool:
    logger.info(f"FASTAPI Services - validate_token() - Validate if JWT token is valid")
    is_expired = True
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        # Check if token has expired
        current_time = str(datetime.datetime.now(timezone.utc))
        if current_time < payload['expiration']:
            is_expired = False
        return is_expired

    except Exception as e:
        logger.error(f"FASTAPI Services Error - validate_token() encountered an error: {e}") 

# Token verification wrapper function
async def verify_token(token: str = Depends(oauth2_scheme)) -> str:
    '''A wrapper to validate the tokens in the request headers'''

    if not token:
        raise HTTPException(
            status_code  = status.HTTP_401_UNAUTHORIZED,
            detail       = {
                'status'    : status.HTTP_204_NO_CONTENT,
                'type'      : "string",
                'message'   : "Missing authentication token"
            },
            headers      = {"WWW-Authenticate": "Bearer"},
        )

    if validate_token(token):
        raise HTTPException(
            status_code  = status.HTTP_401_UNAUTHORIZED,
            detail       = {
                'status'    : status.HTTP_401_UNAUTHORIZED,
                'type'      : "string",
                'message'   : "Invalid or expired token"
            },
            headers      = {"WWW-Authenticate": "Bearer"},
        )
    
    return token 


# Helper function to verify passwords
def verify_password(plain_password: str, hashed_password: str) -> bool:
    logger.info(f"FASTAPI Services - verify_password() - Verifying passwords")
    rehashed_pass= get_password_hash(plain_password)
    return rehashed_pass == hashed_password


# Helper function to count tokens
def count_tokens(text: str) -> int:
    logger.info(f"FASTAPI Services - count_tokens() - Count token for GPT-4o model")
    encoding = tiktoken.encoding_for_model("gpt-4o")
    return len(encoding.encode(text))

# Helper function to provide rectification strings
def rectification_helper() -> str:
    logger.info(f"FASTAPI Services - rectification_helper() - Adding prompt to generate correct answer")
    return "The answer you provided is incorrect. I have attached the question and the steps to find the correct answer for the question. Please perform them and report the correct answer."


# Helper function to generate response restriction
def generate_restriction(final_answer: str) -> str:
    logger.info(f"FASTAPI Services - generate_restriction() - Generating response restriction")
    words = final_answer.split()
    if len(words) <= 10:
        return f"Restrict your response to {len(words)} words only. No yapping."
    elif final_answer.replace(" ", "").isdigit():
        return "Provide only numerical values in your response. No yapping."
    else:
        return "No yapping."
    
# Helper function to check if object is json serializable
def json_serial(obj):
    logger.info(f"FASTAPI Services - json_serial() - JSON serializer for objects not serializable by default json code")
    if isinstance(obj, datetime.datetime):
        try:
            return obj.isoformat()
        except:
            return str(obj)
    return str(obj)

# Function to store the JWT token in the database
def store_tokens(token: str) -> bool:
    logger.info(f"FASTAPI Services - store_tokens() - Store the newly generated token in the database")
    logger.info("FASTAPI Services - store_tokens() - Request to store JWT token to the database received")
    token_saved = False

    conn = create_connection_to_snowflake()

    if conn is None:
        return JSONResponse({
            'status': status.HTTP_503_SERVICE_UNAVAILABLE,
            'type': 'string',
            'message': 'Database not found'
        })
    
    if conn:
        try:
            # Get the user_id from the token and save it to the users table
            decoded_token = decode_jwt_token(token)
            logger.info("FASTAPI Services - store_tokens() - SQL - Running a UPDATE statement")

            cursor = conn.cursor()
            update_query = "UPDATE users SET jwt_token = %s WHERE user_id = %s"
            cursor.execute(update_query, (str(token), decoded_token['user_id']))
            conn.commit()

            logger.info("FASTAPI Services - store_tokens() - SQL - UPDATE statement complete")
            logger.info("FASTAPI Services - store_tokens() - SQL - Saved JWT token to the database")
            token_saved = True

        except Exception as exception:
            logger.error("FASTAPI Services Error: store_tokens() encountered an error")
            logger.error(exception)

        finally:
            close_connection(conn, cursor)
            return token_saved
    
# Helper function to check if user already exists
def check_if_user_already_exists(email):
    logger.info(f"FASTAPI Services - check_if_user_already_exists() - Checking if the user with email id already exists")
    conn = create_connection_to_snowflake()

    if conn is None:
        return JSONResponse({
            'status': status.HTTP_503_SERVICE_UNAVAILABLE,
            'type': 'string',
            'message': 'Database not found'
        })
    
    if conn:
        logger.info(f"FASTAPI Services - check_if_user_already_exists() - Database connection successful")
        cursor = conn.cursor()
        try:
            logger.info(f"FASTAPI Services - SQL - check_if_user_already_exists() - Executing SELECT statement")
            query = """
            SELECT * FROM users WHERE email = %s;
            """
            cursor.execute(query, (email,))
            logger.info(f"FASTAPI Services - SQL - check_if_user_already_exists() - SELECT statement executed successfully")

            db_user = cursor.fetchone()

            # User does not exist with the given email
            if db_user is None:
                close_connection(conn, cursor)
                logger.info(f"FASTAPI Services - Database - check_if_user_already_exists() - Connection to DB closed")
                return None
            else:
                logger.info(f"FASTAPI Services - Database - check_if_user_already_exists() - User already exists with details {db_user}")
                return db_user
        
        except Exception as e:
            logger.error(f"FASTAPI Services Error - check_if_user_already_exists() encountered an error: {e}")  
    return None

# Helper function to Register New User
def register_user(first_name, last_name, phone, email, password):
    logger.info(f"FASTAPI Services - register_user() - Registering User data into the database")
    conn = create_connection_to_snowflake()

    if conn is None:
        return JSONResponse({
            'status': status.HTTP_503_SERVICE_UNAVAILABLE,
            'type': 'string',
            'message': 'Database not found'
        })
    
    if conn:
        logger.info(f"FASTAPI Services - register_user() - Database connection successful")
        cursor = conn.cursor()
        try:
            hashed_password = get_password_hash(password)
            logger.info(f"FASTAPI Services - SQL - register_user() - Executing INSERT statement")
            query = """
            INSERT INTO users(first_name, last_name, phone, email, password)  
            VALUES (%s, %s, %s, %s, %s)
            """

            cursor.execute(query, (first_name, last_name, phone, email, hashed_password))
            conn.commit()
            logger.info(f"FASTAPI Services - SQL - register_user() - INSERT statement executed")

            # Retrieve the ID of the newly registered user
            cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
            new_user_id = cursor.fetchone()[0]
            logger.info(f"FASTAPI Services - register_user() - New user registered with ID: {new_user_id}")

            # Create JWT token for new user
            jwt_token = create_jwt_token({
                'user_id' : new_user_id,
                'email'   : email
            })
            
            token_saved = store_tokens(jwt_token['token'])

            if token_saved:
                logger.info(f"FASTAPI Services - register_user() - JWT token created and stored")
                response = {
                    'status': status.HTTP_200_OK,
                    'type'  : 'string',
                    'message' : jwt_token
                }
            else:
                logger.info(f"FASTAPI Services - register_user() - Failed to save JWT token to database")
                response = {
                    "status"      : status.HTTP_304_NOT_MODIFIED,
                    'type'        : "string",
                    "message"     : "Failed to save token to database"
                }
            
            
        except Exception as e:
            logger.error(f"FASTAPI Services Error - register_user() encountered an error: {e}")  
            response = {
                    "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'type': "string",
                    "message": "New user could not be registered. Something went wrong.",
                }
        finally:
            close_connection(conn, cursor)
            logger.info(f"FASTAPI Services - register_user() - Database - Connection to the database was closed")

        return JSONResponse(content = response)
    
# Helper function to LogIn
def login_user(db_user, email, password):
    logger.info(f"FASTAPI Services - login_user() - Registering User data into the database")
    conn = create_connection_to_snowflake()

    if conn is None:
        return JSONResponse({
            'status': status.HTTP_503_SERVICE_UNAVAILABLE,
            'type': 'string',
            'message': 'Database not found'
        })
    
    if conn:
        logger.info(f"FASTAPI Services - login_user() - Database connection successful")
        cursor = conn.cursor()
        try:

            if verify_password(password, db_user['password']):
                # Create a JWT token for the user after successful authentication
                logger.info(f"FASTAPI Services - login_user() - Password Verified")
                jwt_token = create_jwt_token({
                    "user_id"   : db_user['user_id'], 
                    "email"     : db_user['email']
                })

                token_saved = store_tokens(conn, jwt_token['token'])

                if token_saved:
                    logger.info(f"FASTAPI Services - login_user() - JWT token created and stored")
                    logger.info(f"User logged in: {db_user['user_id']}")
                    response = {
                        "status"      : status.HTTP_200_OK,
                        'type'        : "string",
                        "message"     : jwt_token
                    }
                
                else:
                    logger.info(f"FASTAPI Services - login_user() - Failed to save JWT token to database")
                    response = {
                    "status"      : status.HTTP_304_NOT_MODIFIED,
                    'type'        : "string",
                    "message"     : "Failed to save token to database"
                }

            else:
                logger.error(f"FASTAPI Services - login_user() - Invalid email or password")
                response = {
                        'status'    : status.HTTP_401_UNAUTHORIZED,
                        'type'      : "string",
                        'message'   : "Invalid email or password"
                    }

        except Exception as e:
            logger.error(f"FASTAPI Services Error - login_user() encountered an error: {e}")  
            response = {
                    "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'type': "string",
                    "message": "User could not be logged in. Something went wrong.",
                }

        finally:
            close_connection(conn, cursor)
            logger.info(f"FASTAPI Services - login_user() - Database - Connection to the database was closed")

        # Return the JSON response containing the JWT token
        return JSONResponse(content=response)

# Helper function to get the list of documents
def explore_documents(prompt_count):
    logger.info(f"FASTAPI Services - explore_documents() - Listing out the documents")
    conn = create_connection_to_snowflake()

    if conn is None:
        return JSONResponse({
            'status': status.HTTP_503_SERVICE_UNAVAILABLE,
            'type': 'string',
            'message': 'Database not found'
        })
    
    if conn:
        logger.info(f"FASTAPI Services - explore_documents() - Database connection successful")
        cursor = conn.cursor(DictCursor)
        try:
            logger.info(f"FASTAPI Services - SQL - explore_documents() - Executing SELECT statement")
            query = """
            SELECT document_id, title, image_url, FROM publications_info LIMIT %s
            """
            cursor.execute(query, (prompt_count,))
            rows = cursor.fetchall()
            logger.info(f"FASTAPI Services - SQL - explore_documents() - Output - {rows}")

            response = {
                    'status'    : status.HTTP_200_OK,
                    'type'      : "json",
                    'message'   : [{"document_id": row["DOCUMENT_ID"], "title": row['TITLE'], "image_url": row['IMAGE_URL']} for row in rows],
                    'length'    : prompt_count
            }

            logger.info(f"FASTAPI Services - SQL - explore_documents() - SELECT statement executed successfully")
            
            return JSONResponse(content = response)

        except Exception as e:
            logger.error(f"FASTAPI Services Error - explore_documents() encountered an error: {e}")  

        finally:
            close_connection(conn, cursor)
            logger.info(f"FASTAPI Services - explore_documents() - Database - Connection to the database was closed")


        return JSONResponse({
            'status'    : status.HTTP_500_INTERNAL_SERVER_ERROR,
            'type'      : "string",
            'message'   : "Could not fetch the list of prompts. Something went wrong."
        })


def load_document(document_id):
    logger.info(f"FASTAPI Services - load_document() - Loading the user selected document")
    conn = create_connection_to_snowflake()

    if conn is None:
        return JSONResponse({
            'status': status.HTTP_503_SERVICE_UNAVAILABLE,
            'type': 'string',
            'message': 'Database not found'
        })
    
    if conn:
        logger.info(f"FASTAPI Services - load_document() - Database connection successful")
        cursor = conn.cursor()
        try:
            logger.info(f"FASTAPI Services - SQL - load_document() - Executing SELECT statement")
            query = """
            SELECT * FROM publications_info WHERE document_id = %s;
            """
            cursor.execute(query, (document_id,))
            record = cursor.fetchone()
            logger.info(f"FASTAPI Services - SQL - load_document() - SELECT statement executed successfully")

            if record is None:
                close_connection(conn, cursor)
                logger.info("FASTAPI Services - Database - load_document() - Connection to the database was closed")
                return JSONResponse(
                    {
                        'status'  : status.HTTP_404_NOT_FOUND,
                        'type'    : 'string',
                        'message' : f"Could not fetch the details for the given document_id {document_id}"
                    }
                )
            close_connection(conn, cursor)
            logger.info(f"FASTAPI Services - load_document() - Database - Connection to the database was closed")

            return JSONResponse({
                'status' : status.HTTP_200_OK,
                'type'   : 'json',
                'message': record
            })                       

        except Exception as e:
            logger.error(f"FASTAPI Services Error - load_document() encountered an error: {e}")  

        finally:
            close_connection(conn, cursor)
            logger.info(f"FASTAPI Services - load_document() - Database - Connection to the database was closed")

        return JSONResponse({
            'status'    : status.HTTP_500_INTERNAL_SERVER_ERROR,
            'type'      : "string",
            'message'   : "Could not fetch the user selected document. Something went wrong."
        })
    
def download_files_from_s3(document_id):
    logger.info(f"FASTAPI Services - download_files_from_s3() - Downloading files from s3 bucket to local")
    logger.info(f"FASTAPI Services - download_files_from_s3() - Creating S3 Client")

    # Create S3 Client
    s3_client = boto3.client(
        's3',
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    )

    logger.info(f"FASTAPI Services - download_files_from_s3() - S3 Client created")

    bucket_name = os.getenv("BUCKET_NAME")
    s3_folder_path = f"{bucket_name}/{document_id}"
    local_dir = os.path.join(os.getcwd(), 'downloads', document_id)

    if not os.path.exists(local_dir):
        logger.info(f"FASTAPI Services - download_files_from_s3() - Creating local directory to store the files in {document_id}")
        os.makedirs(local_dir)

    try:
        response = s3_client.list_objects_v2(Bucket = bucket_name, Prefix = document_id)
        logger.info(f"FASTAPI Services - download_files_from_s3() - Listed all files in {document_id}")

        if 'Contents' not in response:
            logger.info(f"FASTAPI Services - download_files_from_s3() - No files found in specified folder path: s3://{bucket_name}/{s3_folder_path}")
            return JSONResponse({
                'status' : 404,
                'type'   : 'string',
                'message' : 'No files found in the specified folder path'
            })
         # s3://publications-info/document_id/
        for obj in response['Contents']:
            file_key = obj['Key']
            file_name = os.path.join(local_dir, os.path.basename(file_key))
            logger.info(f"FASTAPI Services - download_files_from_s3() - Downloading files")
            s3_client.download_file(bucket_name, file_key, file_name)
            logger.info(f"FASTAPI Services - download_files_from_s3() - Downloaded {file_name}")
        
        return JSONResponse({
            'status' : 200,
            'type' : 'string',
            'message' : 'Files downloaded successfully'
        })
              
    except Exception as e:
        logger.error(f"FASTAPI Services Error - download_files_from_s3() encountered an error: {e}")
        return JSONResponse({
            'status' : 500,
            'type': 'string',
            'message' : 'An error occured while downloading files from S3'
        })
    
def extract_text_from_document(document_id):
    logger.info(f"FASTAPI Services - extract_text_from_document() - Extracting text from document with id = {document_id}")

    pdf_dir = os.path.join(os.getcwd(), 'downloads', str(document_id))

    if not os.path.exists(pdf_dir):
        logger.error(f"FASTAPI Services Error - extract_text_from_document() - Directory {pdf_dir} does not exist")
        return None
    
    pdf_file = None
    for file in os.listdir(pdf_dir):
        if file.endswith('.pdf'):
            pdf_file = os.path.join(pdf_dir, file)
            break
    
    if pdf_file is None:
        logger.error(f"FASTAPI Services Error - extract_text_from_document() - No PDF file found in directory {pdf_dir} ")
        return None
    
    try:
        logger.info(f"FASTAPI Services - extract_text_from_document() - Extracting text from pdf file = {pdf_file}")
        text = ""
        with open(pdf_file, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
        print("Text extracted for the entire PDF")
        logger.info(f"FASTAPI Services - extract_text_from_document() - Text extracted for the entire PDF file = {pdf_file}")
        return text.strip()
    
    except Exception as e:
        logger.error(f"FASTAPI Services Error - extract_text_from_document() encountered an error: {e}")

def generate_summary(document_id):
    logger.info(f"FASTAPI Services - generate_summary() - Generating summary for document {document_id}")

    # Extracting text from the document pdf file
    text = extract_text_from_document(document_id)
    logger.info(f"FASTAPI Services - generate_summary() - {document_id} - Text extracted and ready for summarization")

    try:
        # Creating OpenAI client
        client = OpenAI(
            base_url = os.getenv("NVIDIA_URL_SUMMARY"),
            api_key = os.getenv("NVIDIA_API_KEY_SUMMARY")
        )
        logger.info(f"FASTAPI Services - generate_summary() - OpenAI Client created successfully")

        message = [{'role': 'user', 'content' : f"Conclude the summary in 3-5 sensible complete sentences for text, no extra context needed: \n {text}"}]
        logger.info(f"FASTAPI Services - generate_summary() - Message/Prompt created successfully")

        completion = client.chat.completions.create(
            model = "meta/llama-3.1-405b-instruct",
            messages = message,
            temperature = 0.2, 
            top_p = 0.7,
            max_tokens = 150,
            stream = True
        )
        logger.info(f"FASTAPI Services - generate_summary() - NVIDIA model defined successfully")

        summary = ""
        for chunk in completion:
            if chunk.choices[0].delta.content is not None:
                logger.info(f"FASTAPI Services - generate_summary() - Collecting generated summary")
                summary += chunk.choices[0].delta.content
        logger.info(f"FASTAPI Services - generate_summary() - {document_id} - Summary generated successfully")
        return JSONResponse({
            'status' : 200,
            'type' : 'text',
            'message' : summary
        })

    except Exception as e:
        logger.error(f"FASTAPI Services Error - generate_summary() encountered an error: {e}")
        return JSONResponse({
            'status' : 500,
            'type' : 'string',
            'message' : 'Error while generating summary for the pdf document'
        })


