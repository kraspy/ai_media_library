from django.utils import translation
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

from apps.learning.history import DjangoChatMessageHistory

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
    Uses langchain.agents.create_agent (v1.0) and DjangoChatMessageHistory.
    """

    def __init__(self):
        self.llm = get_llm(temperature=0.7)
        self.tools = [search_knowledge_base, get_study_plan]

        from apps.core.models import ProjectSettings

        settings = ProjectSettings.load()
        self.system_prompt = settings.tutor_prompt

        # Inject Language Instruction
        current_language = translation.get_language()
        self.system_prompt += f"\n\nIMPORTANT: Chat with the user in language code: '{current_language}'."

        self.graph = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self.system_prompt,
        )

    def run(self, user_input: str, session_id: str) -> str:
        history = DjangoChatMessageHistory(session_id=session_id)

        user_msg = HumanMessage(content=user_input)
        history.add_message(user_msg)

        messages = history.messages

        result = self.graph.invoke({'messages': messages})

        final_messages = result.get('messages', [])
        if not final_messages:
            return 'Error: No response from agent.'

        last_message = final_messages[-1]

        history.add_message(last_message)

        return last_message.content
