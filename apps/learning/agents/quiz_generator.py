from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from apps.learning.schemas import QuizSchema

from .base import get_llm


class QuizGenerationAgent:
    """
    Agent responsible for generating quiz questions.
    """

    def __init__(self):
        self.llm = get_llm(temperature=0.4)
        self.parser = PydanticOutputParser(pydantic_object=QuizSchema)

    def run(
        self,
        concept_title: str,
        concept_description: str,
        context_text: str = '',
    ) -> QuizSchema:
        prompt = ChatPromptTemplate.from_messages(
            [
                ('system', 'You are an expert exam creator.'),
                (
                    'system',
                    "Generate multiple-choice questions to test the user's understanding of the concept.",
                ),
                (
                    'system',
                    'Ensure distractors (wrong answers) are plausible but incorrect.',
                ),
                ('system', '{format_instructions}'),
                (
                    'user',
                    f'Concept: {concept_title}\nDefinition: {concept_description}\nContext: {context_text}\n\nGenerate 3 questions.',
                ),
            ]
        )

        chain = prompt | self.llm | self.parser

        return chain.invoke(
            {'format_instructions': self.parser.get_format_instructions()}
        )
