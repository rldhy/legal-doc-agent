from pydantic import BaseModel, Field


class LegalAnswer(BaseModel):
    answer: str = Field(
        description="Answer to the user's question based only on retrieved sources."
    )

    citations: list[int] = Field(
        description="Source numbers that support the answer."
    )

    insufficient_evidence: bool = Field(
        description="True if the provided sources are insufficient to answer.",
        default=False
    )
