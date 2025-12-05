from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from apps.core.models import ProjectSettings
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
        settings = ProjectSettings.load()
        system_prompt = settings.concept_extraction_prompt

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    'system',
                    system_prompt,
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
