from pydantic import BaseModel, Field


class GenerateReportRequest(BaseModel):
    construct_evaluation_id: str


class GenerateReportResponse(BaseModel):
    report_id: str
    assessment_result_id: str
    overall_confidence: float
pre=1.0
