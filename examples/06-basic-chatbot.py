from langchain_community.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler    
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate

llm = Ollama(model="llama2",
             base_url="http://192.168.1.68:11434",
             callback_manager = CallbackManager([StreamingStdOutCallbackHandler()]))

prompt = PromptTemplate(input_variables=['history', 'input'], 
                        template='''The following is a friendly conversation between a human and an AI. 
                                    The AI is talkative and provides lots of specific details from its context. 
                                    If the AI does not know the answer to a question, it truthfully says it does not know.\n\n
                                    Current conversation:\n{history}\nHuman: {input}\nAI:''')

prompt2 = PromptTemplate(input_variables=['history', 'input'], 
                        template='''The following is a scientific conversation between a human and an AI.
                                    The AI uses a professorial tone.
                                    The AI is precise and answers in short sentences. 
                                    If the AI does not know the answer to a question, it truthfully says it does not know.\n\n
                                    Current conversation:\n{history}\nHuman: {input}\nAI:''')

chain = ConversationChain(llm=llm, 
                          prompt=prompt2)


while True:
    query = input("\n\nYou: ")
    print()
    chain.invoke(query)
