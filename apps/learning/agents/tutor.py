from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

from .base import get_llm


@tool
def search_knowledge_base(query: str) -> str:
    """Search the knowledge base for relevant information."""
    from apps.library.services.rag_service import RAGService

    service = RAGService()
    results = service.search(query)

    if not results:
        return 'No relevant information found in the knowledge base.'

    formatted_results = '\n'.join(
        [f'- {doc.page_content[:200]}...' for doc in results]
    )
    return f'Found relevant info:\n{formatted_results}'


@tool
def get_study_plan(user_id: int) -> str:
    """Get the current active study plan for the user."""
    from apps.learning.models import StudyPlan

    plan = StudyPlan.objects.filter(status=StudyPlan.Status.ACTIVE).last()

    if not plan:
        return 'No active study plan found.'

    units_text = '\n'.join(
        [f'{u.order}. {u.concept.title}' for u in plan.units.all()]
    )
    return f'Current Plan: {plan.title}\nUnits:\n{units_text}'


class TutorAgent:
    """
    Interactive Tutor Agent that can use tools to help the user.
    """

    def __init__(self):
        self.llm = get_llm(temperature=0.7)
        self.tools = [search_knowledge_base, get_study_plan]

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    'system',
                    "You are a helpful AI Tutor. Use the available tools to answer the user's questions.",
                ),
                ('placeholder', '{chat_history}'),
                ('user', '{input}'),
                ('placeholder', '{agent_scratchpad}'),
            ]
        )

        self.agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(
            agent=self.agent, tools=self.tools, verbose=True
        )

    def run(self, user_input: str, chat_history: list = []) -> str:
        return self.agent_executor.invoke(
            {'input': user_input, 'chat_history': chat_history}
        )['output']
