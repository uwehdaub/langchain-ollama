from langchain_community.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler    
from langchain.chains import ConversationChain

llm = Ollama(model="llama2",
             #base_url="http://192.168.1.68:11434",
             callback_manager = CallbackManager([StreamingStdOutCallbackHandler()]))

chain = ConversationChain(llm=llm, verbose=False)

while True:
    query = input("\n\nYou: ")
    print()
    chain.invoke(query)
