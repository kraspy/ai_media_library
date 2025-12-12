from django.utils import translation
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from apps.core.models import ProjectSettings
from apps.learning.schemas import ConceptSchema, StudyPlanSchema

from .base import get_llm


class PlanGenerationAgent:
    """
    Agent responsible for creating a study plan from a list of concepts.
    """

    def __init__(self):
        self.llm = get_llm(temperature=0.2)
        self.parser = PydanticOutputParser(pydantic_object=StudyPlanSchema)

    def run(
        self,
        concepts: list[ConceptSchema],
        topic_name: str,
        topic_context: str = '',
    ) -> StudyPlanSchema:
        concepts_text = '\n'.join(
            [
                f'- {c.title}: {c.description} (Complexity: {c.complexity})'
                for c in concepts
            ]
        )

        settings = ProjectSettings.load()
        system_prompt = settings.plan_generation_prompt

        if topic_context:
            system_prompt += f'\n\nContext Topic: {topic_context}'

        current_language = translation.get_language()
        system_prompt += f"\n\nIMPORTANT: Provide all Output (Titles, Descriptions) in language: '{current_language}'."

        prompt = ChatPromptTemplate.from_messages(
            [
                ('system', '{system_prompt}'),
                ('system', '{format_instructions}'),
                (
                    'user',
                    "Create a study plan for the topic '{topic_name}' using these concepts:\n\n{concepts_text}",
                ),
            ]
        )

        chain = prompt | self.llm | self.parser

        return chain.invoke(
            {
                'system_prompt': system_prompt,
                'format_instructions': self.parser.get_format_instructions(),
                'topic_name': topic_name,
                'concepts_text': concepts_text,
            }
        )
