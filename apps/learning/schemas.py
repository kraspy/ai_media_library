from pydantic import BaseModel, Field


class ConceptSchema(BaseModel):
    """Schema for an atomic concept extracted from text."""

    title: str = Field(..., description='The title of the concept.')
    description: str = Field(
        ..., description='A concise definition or description of the concept.'
    )
    complexity: int = Field(
        ...,
        description='Complexity level from 1 (simple) to 5 (advanced).',
        ge=1,
        le=5,
    )


class ConceptListSchema(BaseModel):
    """List of extracted concepts."""

    concepts: list[ConceptSchema] = Field(
        ..., description='List of extracted concepts.'
    )


class StudyUnitSchema(BaseModel):
    """Schema for a single unit in a study plan."""

    concept_title: str = Field(
        ..., description='Title of the concept to study in this unit.'
    )
    order: int = Field(
        ..., description='The sequential order of this unit in the plan.'
    )
    description: str = Field(
        ...,
        description='Brief description of what will be covered in this unit.',
    )


class StudyPlanSchema(BaseModel):
    """Schema for a generated study plan."""

    title: str = Field(..., description='Title of the study plan.')
    units: list[StudyUnitSchema] = Field(
        ..., description='Ordered list of study units.'
    )


class QuizQuestionSchema(BaseModel):
    """Schema for a single quiz question."""

    question: str = Field(..., description='The question text.')
    options: list[str] = Field(
        ...,
        description='List of possible answers (distractors + correct answer).',
    )
    correct_index: int = Field(
        ...,
        description='The index of the correct answer in the options list (0-based).',
    )
    explanation: str = Field(
        ..., description='Explanation of why the answer is correct.'
    )


class QuizSchema(BaseModel):
    """Schema for a generated quiz."""

    questions: list[QuizQuestionSchema] = Field(
        ..., description='List of quiz questions.'
    )
