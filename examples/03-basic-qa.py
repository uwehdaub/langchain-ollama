from langchain_community.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler 
                                 
llm = Ollama(model="llama2",
             callback_manager = CallbackManager([StreamingStdOutCallbackHandler()]))

while True:
    query = input("\n\nYou: ")
    print()
    llm.invoke(query)
