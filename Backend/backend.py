from langchain_openai import ChatOpenAI
from langchain import hub
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import UploadFile, Form
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain_text_splitters.character import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import JinaEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.schema import Document
from docx import Document as wordDocument
from transformers import BlipProcessor, BlipForConditionalGeneration, BlipForQuestionAnswering
from PIL import Image
from langchain_community.document_loaders import PyMuPDFLoader



import os
import io
import numpy as np
import torch
from fastapi import Request

np.random.seed(42)
all_image_features = np.random.randn(1000, 512).astype(np.float32)


load_dotenv()
open_api_key = os.getenv("ZHIPU_API_KEY")
app = FastAPI()

template = """you are a AI assistant chat with human with humorous tongue.
{chat_history}
Human:{human_input}
AI:
"""

prompt = PromptTemplate(input_variables=["chat_history", "human_input"], template=template)

memory = ConversationBufferMemory(memory_key="chat_history")

# class MessageRequest(BaseModel):
#     message:str
#     value1:bool

#部署大模型
llm = ChatOpenAI(
    model="glm-4",
    openai_api_key=open_api_key,
    openai_api_base="https://open.bigmodel.cn/api/paas/v4"
)

embeddings = JinaEmbeddings(
    model_name="jina-embeddings-v4",
    jina_api_key=os.getenv("JINA_API_KEY")
)

#这种写法已经被弃用，改进写法
# llm_chain = LLMChain(
#     llm=llm,
#     memory=memory
# )

llm_chain = prompt | llm

tools = load_tools(["serpapi"], llm=llm)

conversational_react_agent = initialize_agent(
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    tools=tools,
    llm=llm,
    verbose=True,
    max_iterations = 3,
    handle_parsing_errors = True,
    memory=memory
)

#允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def format_docs(docs):
    return "\\n\\n".join(doc.page_content for doc in docs)

#接受前端post请求，调大模型生成回复,并可以记住用户的前几次对话
@app.post("/chat")
async def chat(
        message: str = Form(...),
        value1: str = Form(...),
        files: list[UploadFile] = Form(default=[])
):
    if value1 == "true":

        response = conversational_react_agent(message)
        return {"reply": response["output"]}

    # 如果上传了文件，则结合用户输入生成模板，进行RAG
    elif len(files) > 0:
        all_splits = []
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

        processor = BlipProcessor.from_pretrained("Salesforce/blip-vqa-base")
        model = BlipForQuestionAnswering.from_pretrained("Salesforce/blip-vqa-base")

        for file in files:
            root, ext = os.path.splitext(file.filename)
            match ext:
                case ".txt":
                    content = await file.read()
                    text = content.decode("utf-8")
                case ".docx":
                    content = await file.read()
                    with open("temp.docx", "wb") as f:
                        f.write(content)
                    doc = wordDocument("temp.docx")
                    text = "\n".join([p.text for p in doc.paragraphs])
                case ".pdf":
                    content = await file.read()
                    with open("temp.pdf", "wb") as f:
                        f.write(content)
                    loader = PyMuPDFLoader("temp.pdf")
                    doc = loader.load()
                    text = "\n".join([d.page_content for d in doc])
                case ".jpg":
                    img_bytes = await file.read()
                    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                    inputs = processor(image, message, return_tensors="pt")
                    output = model.generate(**inputs, max_new_tokens=50, num_beams=5)
                    caption = processor.decode(output[0], skip_special_tokens=True)
                    return {"reply": caption}
            doc = Document(page_content=text, metadata={"filename": file.filename})
            all_splits.extend(text_splitter.split_documents([doc]))
        vectorstore = Chroma.from_documents(documents=all_splits, embedding=embeddings)
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 6})
        file_prompt = hub.pull("rlm/rag-prompt")
        rag_chain = (
                {"context": retriever | format_docs, "question": RunnablePassthrough()}
                | file_prompt
                | llm
                | StrOutputParser()
        )
        response = rag_chain.stream(message)
        response = "".join(response)
        return {"reply": response}

    else:
        response = llm_chain.invoke(
            {
                "human_input": message,
                "chat_history": memory.load_memory_variables({})["chat_history"]
            }
        )
        memory.save_context({"input": message}, {"output": response.content})
        return {"reply": response.content}

@app.post("/reset")
async def reset(request:Request):
    data = await request.json()
    if data.get("new_session"):
        memory.clear()