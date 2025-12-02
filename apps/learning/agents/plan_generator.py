from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

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
        self, concepts: list[ConceptSchema], topic_name: str
    ) -> StudyPlanSchema:
        concepts_text = '\n'.join(
            [
                f'- {c.title}: {c.description} (Complexity: {c.complexity})'
                for c in concepts
            ]
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ('system', 'You are an expert curriculum designer.'),
                (
                    'system',
                    'Create a logical, step-by-step study plan based on the provided concepts.',
                ),
                (
                    'system',
                    'Order the units from simplest to most complex. Ensure dependencies are respected.',
                ),
                ('system', '{format_instructions}'),
                (
                    'user',
                    f"Create a study plan for the topic '{topic_name}' using these concepts:\n\n{concepts_text}",
                ),
            ]
        )

        chain = prompt | self.llm | self.parser

        return chain.invoke(
            {'format_instructions': self.parser.get_format_instructions()}
        )
