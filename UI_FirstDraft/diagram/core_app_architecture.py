from diagrams import Diagram, Edge, Cluster 
from diagrams.aws.storage import S3 
from diagrams.saas.analytics import Snowflake
from diagrams.onprem.workflow import Airflow 
from diagrams.programming.framework import FastAPI 
from diagrams.programming.flowchart import Inspection
from diagrams.custom import Custom 
from diagrams.onprem.client import Users 


with Diagram("Assignment 3 Architecture", show = False):
    
    # Define nodes
    users           = Users("End Users")
    question        = Inspection("Question")
    streamlit_app   = Custom("Streamlit", "./images/Streamlit.png") 
    
    cfa_institute   = Custom("Data Source \n Website - CFA Institute", "./images/cfa-institute.png")
    pdf             = Custom("PDF Documents \n and images", "./images/PDF_documents.png")
    scraper         = Airflow("Content Extractor")
    airflow         = Airflow("Airflow \n Snowflake and S3 uploader") 
    s3_1            = S3("AWS S3\n(Images, PDFs)")
    s3_2            = S3("AWS S3\n(Images, PDFs)")
    snowflake       = Snowflake("Snowflake DB")
    
    fastapi         = FastAPI("FastAPI")
    pdf2            = Custom("PDF Document", "./images/PDF_documents.png")
    unstructured    = Custom("Unstructured\nParsing PDFs \nwith\nMachine Learning", "./images/Unstructured.png")
    extracted_text  = Custom("Text", "./images/Text.png")
    extracted_image = Custom("Images, Tables", "./images/PNG.png")
    openai_embed    = Custom("OpenAI\nEmbeddings", "./images/OpenAI.png")
    chromadb        = Custom("ChromaDB\nVector Store", "./images/Chroma.png")
    openai_llm1     = Custom("Image Summary\nwith\nGPT-4o", "./images/OpenAI.png")

    


    with Cluster("Data Ingestion & Storage", direction = "LR"):
        cfa_institute >> Edge() >> scraper
        scraper >> Edge() >> pdf
        pdf >> Edge() >> airflow
        airflow >> Edge() >> s3_1
        airflow >> Edge() >> snowflake

    with Cluster("RAG Application", direction = "RL"):
        question << users
        streamlit_app << question
        fastapi << streamlit_app
        fastapi << s3_2
        pdf2 << fastapi
        unstructured << pdf2
        extracted_text << unstructured
        extracted_image << unstructured
        openai_llm1 << extracted_image
        openai_embed << extracted_text
        chromadb << openai_embed
        openai_embed << openai_llm1






    # with Cluster("Data Ingestion & Storage"):
    #     cfa_institute >> Edge(label="Data Source") >> pdf
    #     pdf >> Edge(label="Data Source") >> scraper 
    #     scraper >> Edge(label="Scrape data (CFA Institute)") >> airflow 
    #     airflow >> Edge(label="Upload Images & PDFs") >> s3 
    #     airflow >> Edge(label="Store Metadata") >> snowflake 


    # with Cluster("Client Application", direction="LR"):    
    #     streamlit_app << Edge(label="User Requests") >> fastapi 
    #     fastapi >> Edge(label="Summarization / Multi-modal Query") >> nv_service  
    #     fastapi >> Edge(label="User Interface") >> streamlit_app 
    #     users >> Edge(label="User Interactions") >> streamlit_app 


    # with Cluster("Research Notes Indexing & Search"):
    #     rag_index >> Edge(label="Preprocess Data") >> cleanlabs 
    #     cleanlabs >> Edge(label="Vector Store for Search") >> chroma 
    #     chroma >> Edge(label="Store Research Notes")


    # fastapi >> Edge(label="Search Requests")
    # chroma >> Edge(label="Retrieve Notes") >> fastapi 
    # chroma >> Edge(label="Query Results") >> fastapi 


    # with Cluster("Deployment"):
    #     fastapi - docker 
    #     streamlit_app - docker 