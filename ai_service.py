
import os

from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

load_dotenv()

prompt_template = PromptTemplate.from_template(
    "Write a concise 2-3 sentence marketing caption for this product in a {tone} tone: {description}"
)

llm = ChatOpenAI(
    model_name=os.getenv("OPENAI_MODEL_NAME"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
)

chain = LLMChain(llm=llm, prompt=prompt_template)


def generate_caption_text(description: str, tone: str) -> str:
    result = chain.invoke({"description": description, "tone": tone})
    return result["text"]

