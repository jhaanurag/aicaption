system_prompt = f"try to give a two line caption for this product in this tone: funny and product: Eco-friendly reusable water bottle made from stainless steel"

# enter email validate email send otp verify otp then send auth flow


prompt_template = PromptTemplate.from_template(
    'try to give a two line caption for this product in this tone: {funny} and product: {product}'
)

openai = ChatOpenAI(
    model_name='gpt-4.1-2025-04-14',
    openai_api_key='lol'
)

chain = LLMChain(llm=openai, prompt=prompt_template)

response = chain.invoke(
    input={'funny': 'funny', 'product': 'Eco-friendly reusable water bottle made from stainless steel'}
)

print(response['text'])
