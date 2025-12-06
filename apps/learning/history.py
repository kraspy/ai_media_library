from typing import List

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
)

from apps.learning.models import TutorChatMessage, TutorChatSession


class DjangoChatMessageHistory(BaseChatMessageHistory):
    """
    Chat history implementation that stores messages in Django models.
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self._session = None

    @property
    def session(self):
        if not self._session:
            try:
                self._session = TutorChatSession.objects.get(
                    id=self.session_id
                )
            except TutorChatSession.DoesNotExist:
                raise ValueError(
                    f'Session with ID {self.session_id} not found'
                )
        return self._session

    @property
    def messages(self) -> List[BaseMessage]:
        """Retrieve messages from the database"""
        messages = []
        for msg in self.session.messages.all():
            if msg.role == TutorChatMessage.Role.USER:
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == TutorChatMessage.Role.ASSISTANT:
                messages.append(AIMessage(content=msg.content))
        return messages

    def add_message(self, message: BaseMessage) -> None:
        """Add a message to the database"""
        if isinstance(message, HumanMessage):
            role = TutorChatMessage.Role.USER
        elif isinstance(message, AIMessage):
            role = TutorChatMessage.Role.ASSISTANT
        else:
            return

        TutorChatMessage.objects.create(
            session=self.session, role=role, content=message.content
        )

    def clear(self) -> None:
        """Clear all messages in the session"""
        self.session.messages.all().delete()
