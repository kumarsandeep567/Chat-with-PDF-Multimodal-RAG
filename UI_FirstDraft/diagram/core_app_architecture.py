# Import necessary modules from the diagrams library and other dependencies
import os  # Provides functions to interact with the operating system, here used to check if file paths exist
from diagrams import Diagram, Edge, Cluster  # Diagram, Edge, and Cluster are used to define diagram components and structure
from diagrams.aws.storage import S3  # S3 component icon from AWS library
from diagrams.gcp.database import Bigtable  # Bigtable component icon from GCP library
from diagrams.onprem.database import PostgreSQL  # PostgreSQL icon from on-premises resources
from diagrams.onprem.workflow import Airflow  # Airflow icon for workflow management
from diagrams.programming.framework import FastAPI  # FastAPI icon for backend framework
from diagrams.programming.language import Python  # Python icon for language-based operations
from diagrams.custom import Custom  # Custom allows use of user-defined images as icons
from diagrams.onprem.client import Users  # Icon representing end users or clients

# Define paths to custom images for various components
streamlit_image_path = "/Users/ramyyogeshkumarsolanki/Documents/GitHub/automated_text_extractor/diagram/images/Streamlit.png"
cfa_institute_image_path = "/Users/ramyyogeshkumarsolanki/Documents/GitHub/Assignment3/UI_FirstDraft/diagram/images/cfa-institute.png"
docker_image_path = "/Users/ramyyogeshkumarsolanki/Documents/GitHub/Assignment3/UI_FirstDraft/diagram/images/Docker.png"
nvidia_image_path = "/Users/ramyyogeshkumarsolanki/Documents/GitHub/Assignment3/UI_FirstDraft/diagram/images/Nvidia-Logo.png"
rag_image_path = "/Users/ramyyogeshkumarsolanki/Documents/GitHub/Assignment3/UI_FirstDraft/diagram/images/RAG.png"
cleanlabs_image_path = "/Users/ramyyogeshkumarsolanki/Documents/GitHub/Assignment3/UI_FirstDraft/diagram/images/cleanlab.png"
chroma_image_path = "/Users/ramyyogeshkumarsolanki/Documents/GitHub/Assignment3/UI_FirstDraft/diagram/images/Chroma.png"
snowflake_image_path = "/Users/ramyyogeshkumarsolanki/Documents/GitHub/Assignment3/UI_FirstDraft/diagram/images/Snowflake.png"

# Loop through each image path and check if it exists, printing the result to the console for debugging
for path in [streamlit_image_path, cfa_institute_image_path, docker_image_path, nvidia_image_path, rag_image_path, cleanlabs_image_path, chroma_image_path, snowflake_image_path]:
    print(f"Checking {path}: {os.path.exists(path)}")  # os.path.exists(path) returns True if file exists, False otherwise

# Create a new diagram titled "Assignment 3 Architecture"
# show=False prevents the diagram from opening after creation; direction="LR" makes the diagram flow from left to right
# node_attr sets default styling for the nodes
with Diagram("Assignment 3 Architecture", show=False, direction="LR", node_attr={"fontsize": "10", "margin": "0.1"}, outformat="svg", quiet=True):
    
    # Data Ingestion & Storage Cluster: Handles data ingestion and storage using Airflow, S3, and Snowflake
    with Cluster("Data Ingestion & Storage"):
        airflow = Airflow("Airflow (Pipeline)")  # Airflow as workflow pipeline manager
        scraper = Python("Data Scraper")  # Data scraper component written in Python
        s3 = S3("S3 (Images, PDFs)")  # AWS S3 for storing images and PDFs
        snowflake = Custom("Snowflake DB", snowflake_image_path)  # Snowflake as the main database, with a custom icon
        cfa_institute = Custom("CFA Institute", cfa_institute_image_path)  # CFA Institute as the data source

        # Define relationships between the components within the Data Ingestion & Storage cluster
        cfa_institute >> Edge(label="Data Collection") >> scraper  # Data is collected from CFA Institute to the scraper
        scraper >> Edge(label="Scrape data (CFA Institute)") >> airflow  # Scraped data is sent to Airflow for processing
        airflow >> Edge(label="Upload Images & PDFs") >> s3  # Airflow uploads processed data to S3 storage
        airflow >> Edge(label="Store Metadata") >> snowflake  # Airflow stores metadata in Snowflake

    # Client Application Cluster: Manages user interactions and backend services
    with Cluster("Client Application", direction="RL"):  # Cluster directed from right to left for user flow clarity
        fastapi = FastAPI("FastAPI (Backend)")  # FastAPI as the backend framework
        streamlit_app = Custom("Streamlit", streamlit_image_path)  # Streamlit as the user-facing frontend
        nv_service = Custom("NVIDIA Services\n(Summary, RAG)", nvidia_image_path)  # NVIDIA services for summarization and retrieval-augmented generation (RAG)

        # Define relationships within the Client Application cluster
        streamlit_app << Edge(label="User Requests") >> fastapi  # Streamlit receives user requests and forwards them to FastAPI
        fastapi >> Edge(label="Summarization / Multi-modal Query") >> nv_service  # FastAPI communicates with NVIDIA services

        # Define interactions with end users
        users = Users("End Users")  # Represents end users interacting with the system
        fastapi >> Edge(label="User Interface") >> streamlit_app  # FastAPI sends the UI response back to Streamlit
        users >> Edge(label="User Interactions") >> streamlit_app  # End users interact directly with Streamlit frontend

    # Research Notes Indexing & Search Cluster: Handles data processing and storage for research note indexing and search
    with Cluster("Research Notes Indexing & Search"):
        rag_index = Custom("Multi-modal RAG Index", rag_image_path)  # Multi-modal RAG Index for indexing and retrieval
        cleanlabs = Custom("CleanLabs\n(Data Preprocessing)", cleanlabs_image_path)  # CleanLabs for data preprocessing
        chroma = Custom("Chroma\n(Vector Search)", chroma_image_path)  # Chroma for vector search
        search_engine = Bigtable("Search Index")  # Bigtable as the main search index

        # Define relationships within the Research Notes Indexing & Search cluster
        rag_index >> Edge(label="Preprocess Data") >> cleanlabs  # RAG index passes data to CleanLabs for preprocessing
        cleanlabs >> Edge(label="Vector Store for Search") >> chroma  # Preprocessed data is stored in Chroma for vector search
        chroma >> Edge(label="Store Research Notes") >> search_engine  # Vector-stored notes are added to the search engine

    # Connections from Client Application to Research Notes Indexing & Search cluster
    fastapi >> Edge(label="Search Requests") >> search_engine  # FastAPI sends search requests to Bigtable search engine
    search_engine >> Edge(label="Retrieve Notes") >> fastapi  # Bigtable returns search results to FastAPI
    chroma >> Edge(label="Query Results") >> fastapi  # Chroma returns query results to FastAPI

    # Deployment Cluster: Manages deployment of Docker containers
    with Cluster("Deployment"):
        docker = Custom("Docker", docker_image_path)  # Docker icon representing containerization of the application components
        
        # Define which services are contained within Docker
        fastapi - docker  # FastAPI is containerized in Docker
        streamlit_app - docker  # Streamlit is also containerized in Docker
