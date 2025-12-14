from django.utils import translation
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from apps.core.models import ProjectSettings
from apps.learning.schemas import QuizSchema

from .base import get_llm


class QuizGenerationAgent:
    """
    Agent responsible for generating quiz questions.
    """

    def __init__(self, llm=None):
        self.llm = llm or get_llm(temperature=0.2)
        self.parser = PydanticOutputParser(pydantic_object=QuizSchema)

    def run(
        self,
        concept_title: str,
        concept_description: str,
        context_text: str = '',
        topic_context: str = '',
    ) -> QuizSchema:
        settings = ProjectSettings.load()
        system_prompt = settings.quiz_generation_prompt

        if topic_context:
            system_prompt += f'\n\nContext Topic: {topic_context}'

        current_language = translation.get_language()
        system_prompt += f"\n\nIMPORTANT: Provide all Output (Questions, Options, Explanations) in language: '{current_language}'."

        prompt = ChatPromptTemplate.from_messages(
            [
                ('system', '{system_prompt}'),
                ('system', '{format_instructions}'),
                (
                    'user',
                    'Concept: {concept_title}\nDefinition: {concept_description}\nContext: {context_text}\n\nGenerate 3 questions.',
                ),
            ]
        )

        chain = prompt | self.llm | self.parser

        return chain.invoke(
            {
                'system_prompt': system_prompt,
                'format_instructions': self.parser.get_format_instructions(),
                'concept_title': concept_title,
                'concept_description': concept_description,
                'context_text': context_text,
            }
        )

    async def arun(
        self,
        concept_title: str,
        concept_description: str,
        system_prompt: str,
        context_text: str = '',
        topic_context: str = '',
    ) -> QuizSchema:
        if topic_context:
            system_prompt += f'\n\nContext Topic: {topic_context}'

        current_language = translation.get_language()
        system_prompt += f"\n\nIMPORTANT: Provide all Output (Questions, Options, Explanations) in language: '{current_language}'."

        prompt = ChatPromptTemplate.from_messages(
            [
                ('system', '{system_prompt}'),
                ('system', '{format_instructions}'),
                (
                    'user',
                    'Concept: {concept_title}\nDefinition: {concept_description}\nContext: {context_text}\n\nGenerate 3 questions.',
                ),
            ]
        )

        chain = prompt | self.llm | self.parser

        return await chain.ainvoke(
            {
                'system_prompt': system_prompt,
                'format_instructions': self.parser.get_format_instructions(),
                'concept_title': concept_title,
                'concept_description': concept_description,
                'context_text': context_text,
            }
        )
