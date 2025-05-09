import os
from dotenv import load_dotenv
from langchain_openai.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_core.runnables import RunnableParallel, RunnablePassthrough


load_dotenv()

def get_response_from_model(context,question):
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    model = ChatOpenAI(model="gpt-4", temperature=0.0,openai_api_key=OPENAI_API_KEY)
    parser = StrOutputParser()
    template = """
    Answer the question based on the context below. If you can't answer the question, 
    reply "Désolé , je n'ai aucune idée." Utilise ta faculté de raisonnement pour repondre à des questions externes qu'on te pose concernant les rapports medicaux des patients.
    Context: {context}
    Question: {question}
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    
    with open("context.txt","w") as file:
        file.write(context)
    
    #Load the transcript in memory    
    loader = TextLoader("context.txt")
    text_documents = loader.load()
    
    #Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=150)
    documents = text_splitter.split_documents(text_documents)
    
    # Generate the embeddings for an arbitrary query
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    
    
    #use pinecone as a vector store
    pinecone_index_name = "project"


    pinecone = PineconeVectorStore.from_documents(
    documents=documents, embedding=embeddings, index_name=pinecone_index_name
    )
    
    chain = (
    {"context": pinecone.as_retriever(), "question": RunnablePassthrough()}
    | prompt
    | model
    | parser
    )
    response=chain.invoke(question)
    return response
