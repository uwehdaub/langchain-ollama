from langchain_community.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler 

from langchain.prompts import PromptTemplate
                                 
llm = Ollama(model="llama2",
             callback_manager = CallbackManager([StreamingStdOutCallbackHandler()]))

prompt = PromptTemplate(
    input_variables=["whom"],
    template="Tell me a joke about {whom}.",
)

chain = prompt | llm

#from langchain.chains import LLMChain
#chain = LLMChain(llm=llm, 
#                 prompt=prompt,
#                 verbose=True)

while True:
    query = input("\n\nYou: ")
    print()
    chain.invoke(query)
