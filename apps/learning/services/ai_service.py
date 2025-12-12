from apps.learning.agents.concept_extractor import ConceptExtractionAgent
from apps.learning.agents.plan_generator import PlanGenerationAgent
from apps.learning.agents.quiz_generator import QuizGenerationAgent
from apps.learning.schemas import (
    ConceptListSchema,
    ConceptSchema,
    QuizSchema,
    StudyPlanSchema,
)


class AIService:
    """
    Service layer to interact with AI Agents.
    """

    def extract_concepts(
        self, text: str, topic_context: str = ''
    ) -> ConceptListSchema:
        agent = ConceptExtractionAgent()
        return agent.run(text, topic_context)

    def generate_study_plan(
        self,
        concepts: list[ConceptSchema],
        topic_name: str,
        topic_context: str = '',
    ) -> StudyPlanSchema:
        agent = PlanGenerationAgent()
        return agent.run(concepts, topic_name, topic_context)

    def generate_quiz(
        self,
        concept_title: str,
        concept_description: str,
        context_text: str = '',
        topic_context: str = '',
    ) -> QuizSchema:
        agent = QuizGenerationAgent()
        return agent.run(
            concept_title, concept_description, context_text, topic_context
        )

    async def generate_quiz_async(
        self,
        concept_title: str,
        concept_description: str,
        context_text: str = '',
        topic_context: str = '',
    ) -> QuizSchema:
        agent = QuizGenerationAgent()
        return await agent.arun(
            concept_title, concept_description, context_text, topic_context
        )
