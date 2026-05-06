import os

from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()


class CaptionOutput(BaseModel):
    caption: str = Field(description="A concise 2-3 sentence social media marketing caption")


parser = PydanticOutputParser(pydantic_object=CaptionOutput)

prompt_template = PromptTemplate(
    template=(
        "Create a concise 2-3 sentence social media marketing caption.\n"
        "Product description: {product_description}\n"
        "Campaign tone: {campaign_tone}\n"
        "{format_instructions}"
    ),
    input_variables=["product_description", "campaign_tone"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

llm = ChatOpenAI(
    model_name=os.getenv("OPENAI_MODEL_NAME"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
)

chain = prompt_template | llm | parser


def generate_caption_text(product_description: str, campaign_tone: str) -> str:
    result = chain.invoke(
        {"product_description": product_description, "campaign_tone": campaign_tone}
    )
    return result.caption
