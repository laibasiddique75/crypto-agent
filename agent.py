import os
from dotenv import load_dotenv , find_dotenv
from agents import Agent , Runner , RunConfig , AsyncOpenAI , OpenAIChatCompletionsModel
import chainlit as cl
from tools import get_crypto_price

load_dotenv(find_dotenv())
gemini_api_key = os.getenv("GEMINI_API_KEY")
print("gemini API key loaded:" , gemini_api_key)

client = AsyncOpenAI(
    api_key=gemini_api_key ,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

run_config = RunConfig(
    model = OpenAIChatCompletionsModel(model="gemini-2.0-flash" , openai_client=client),
    model_provider = client,
    tracing_disabled = True ,
)

CryptoDataAgent = Agent(
    name="CryptoDataAgent",
    instructions="you are helpful agent that gives real time cryptocurrency prices using CoinGecKo",
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash" , openai_client=client),
    tools=[get_crypto_price]
)

@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("history" , [])
    await cl.Message(
        content = "Welcome to the cryptocurrency chatbot! \n\nAsk me anything about coins."

    ).send()

@cl.on_message
async def handle_message(message: cl.Message):
    history = cl.user_session.get("history")
    history.append({"role" : "user" , "content":message.content})

    try:
        result = Runner.run_sync(CryptoDataAgent , input=history , run_config=run_config)
        final_output = result.final_output or "❌ Gemini didn't return any response."
    except Exception as e:
        final_output = f"❌ An error occurred: {e}"
    await cl.Message(content=final_output).send()
    history.append({"role": "assistant" , "content": final_output})

    cl.user_session.set("history" , history)
