
import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

load_dotenv()

# flow: enter email validate email -> generate otp -> send otp verify otp then send auth flow

prompt_template = PromptTemplate.from_template(
    'try to give a two line caption for this product in this tone: {funny} and product: {product}'
)

openai = ChatOpenAI(
    model_name=os.getenv('OPENAI_MODEL_NAME'),
    base_url=os.getenv('OPENAI_BASE_URL'),
    openai_api_key=os.getenv('OPENAI_API_KEY')
)

chain = LLMChain(llm=openai, prompt=prompt_template)

response = chain.invoke(
    input={'funny': 'funny', 'product': 'Eco-friendly reusable water bottle made from stainless steel'}
)

print(response['text'])

