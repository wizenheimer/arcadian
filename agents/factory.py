import os
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory
from langchain.llms import Cohere
import pinecone
from langchain.vectorstores import Pinecone
from langchain.embeddings import CohereEmbeddings
from langchain.tools import Tool
from langchain.agents import initialize_agent
from converse.loader import ConversationRepository
from accounts.models import User
from django.contrib.contenttypes.models import ContentType

from converse.models import Conversation


class AgentFactory:
    """
    Factory for creating agent based on Agent Model
    """

    def __init__(self):
        pinecone.init(
            api_key=os.environ.get("PINECONE_API_KEY"),
            environment=os.environ.get("PINECONE_ENV"),
        )
        self.conversation_repository = ConversationRepository()

    async def create_agent(
        self,
        conversation_id,
        max_iterations=5,
        streaming_enabled=False,
        multihop_disabled=False,
        return_intermediate_steps=True,
        handle_parsing_errors=True,
        callback_handler=None,
    ):
        # initialize LLM
        llm = Cohere(cohere_api_key=os.environ.get("COHERE_API_KEY"))

        # initialize Embedding Model
        embeddings = CohereEmbeddings(cohere_api_key=os.environ.get("COHERE_API_KEY"))

        # Load the memory and prepare it with any previous message
        memory = await self.load_memory(conversation_id)

        # preparing the index
        document = conversation.document

        index_name = f"index_doc_{document.id}"
        if index_name not in pinecone.list_indexes():
            docsearch = pinecone.create_index(
                index_name=index_name,
                dimension=1024,
                metric="cosine",
                pods=1,
                replicas=1,
                pod_type="p1.x1",
            )
        docsearch = Pinecone.from_existing_index(index_name, embeddings)

        # initialize the chain
        chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=docsearch.as_retriever(),
            memory=memory,
        )

        # fetch document discription
        conversation = Conversation.objects.get(id=conversation_id)
        document_name = document.name
        folder_tags = document.folder.tags.all()
        # compose chains as tools
        tools = [
            Tool(
                name=f"{document_name}",
                func=chain.run,
                description=f"Useful for answering questions about {document_name}.Tags {folder_tags}",
                return_direct=True,
            ),
        ]

        # prepare agent
        query_agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent="zero-shot-react-description",
            verbose=True,
            max_iterations=max_iterations,
            return_direct=multihop_disabled,
            return_intermediate_steps=return_intermediate_steps,
            handle_parsing_errors=handle_parsing_errors,
            streaming=streaming_enabled,
        )

        return query_agent

    async def load_memory(
        self,
        conversation_id=None,
    ):
        """
        Loads previous conversations into agent's memory
        """
        memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )
        # this implies a new conversation
        if conversation_id is None:
            return memory

        # load message from the conversation
        messages = await self.conversation_repository.get_messages(conversation_id)
        user_model_content_type = ContentType.objects.get_for_model(User)
        # Add the messages to the memory
        for message in messages:
            # if message is created by User
            if (
                ContentType.objects.get_for_model(message.sender)
                == user_model_content_type
            ):
                # Add user message to the memory
                memory.chat_memory.add_user_message(message.content)
            else:
                # Add AI message to the memory
                memory.chat_memory.add_ai_message(message.content)

        return memory
