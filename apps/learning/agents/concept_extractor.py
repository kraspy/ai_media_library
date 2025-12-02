from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from apps.learning.schemas import ConceptListSchema

from .base import get_llm


class ConceptExtractionAgent:
    """
    Agent responsible for extracting atomic concepts from text.
    """

    def __init__(self):
        self.llm = get_llm(temperature=0.0)
        self.parser = PydanticOutputParser(pydantic_object=ConceptListSchema)

    def run(self, text: str) -> ConceptListSchema:
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    'system',
                    'You are an expert educational analyst. Your goal is to extract key concepts from the provided text.',
                ),
                (
                    'system',
                    'Extract atomic concepts that are suitable for creating flashcards and study units.',
                ),
                ('system', '{format_instructions}'),
                (
                    'user',
                    'Analyze the following text and extract the key concepts:\n\n{text}',
                ),
            ]
        )

        chain = prompt | self.llm | self.parser

        return chain.invoke(
            {
                'text': text,
                'format_instructions': self.parser.get_format_instructions(),
            }
        )
