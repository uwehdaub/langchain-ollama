from langchain_community.llms import Ollama
                                 
llm = Ollama(model="llama2")

query = "Tell me a joke about a programmer."
print("You: ", query)

result = llm.invoke(query)

print(result)
print()
