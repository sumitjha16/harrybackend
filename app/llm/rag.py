import logging
from typing import List, Tuple, Dict, Any
from functools import lru_cache
# Updated imports for LangChain
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from app.llm.embeddings import get_vector_store
from app.llm.model import get_llm_model
from app.llm.prompts import get_system_prompt, get_chat_prompt_template, get_summarization_prompt_template
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class RAGChain:
    def __init__(self):
        self.llm = get_llm_model()
        self.vector_store = get_vector_store()
        self.retriever = self.vector_store.as_retriever(
            search_kwargs={"k": settings.RETRIEVAL_K}
        )
        # Fix memory configuration with output_key specification
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer",  # Specify which key to store in memory
            k=5  # Keep only the last 5 exchanges for efficiency
        )

    def get_conversation_chain(self, response_mode: str = "freeform"):
        system_prompt = get_system_prompt(response_mode)

        # Use the predefined chat prompt template from prompts.py
        prompt = get_chat_prompt_template()

        chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.retriever,
            memory=self.memory,
            combine_docs_chain_kwargs={"prompt": prompt.partial(system_prompt=system_prompt)},
            return_source_documents=True,
            chain_type="stuff"
        )
        return chain

    async def generate_response(self, query: str, response_mode: str = "freeform") -> Tuple[str, List[str]]:
        logger.info(f"Generating response for query: {query}")
        chain = self.get_conversation_chain(response_mode)

        # Execute the chain using the updated invoke method
        try:
            # Replace chain() call with chain.invoke()
            result = chain.invoke({"question": query})

            # Extract answer and sources
            answer = result.get("answer", "Sorry, I couldn't generate a response.")
            source_docs = result.get("source_documents", [])
            sources = [doc.metadata.get("source", "Unknown") for doc in source_docs]

            return answer, sources
        except Exception as e:
            logger.error(f"Error in chain execution: {e}")
            return f"I encountered an error while processing your question: {str(e)}", []

    async def generate_summary(self, summary_type: str, summary_target: str, response_mode: str = "structured") -> Tuple[str, List[str]]:
        logger.info(f"Generating {summary_type} summary for: {summary_target}")

        try:
            # Form a better retrieval query
            retrieval_query = f"{summary_type} {summary_target} Harry Potter"
            docs = self.retriever.get_relevant_documents(retrieval_query)

            if not docs:
                return f"Sorry, I couldn't find enough information about {summary_target}.", []

            context = "\n\n".join([doc.page_content for doc in docs])
            system_prompt = get_system_prompt(response_mode)

            # Use the summarization prompt template
            prompt_template = get_summarization_prompt_template()
            prompt_values = {
                "system_prompt": system_prompt,
                "context": context,
                "summary_type": summary_type,
                "summary_target": summary_target
            }
            
            # Format the prompt and send to LLM
            prompt_text = prompt_template.format(**prompt_values)
            response = self.llm(prompt_text)
            sources = [doc.metadata.get("source", "Unknown") for doc in docs]

            return response, sources
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"I encountered an error while generating the summary: {str(e)}", []


@lru_cache()
def get_rag_chain():
    return RAGChain()