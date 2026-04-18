from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict


class Stage4State(TypedDict, total=False):
    mode: str                    # analyze | report | compare | chat
    upload_id: int
    question: str

    upload_meta: Dict[str, Any]
    prediction: Dict[str, Any]
    comparison: Dict[str, Any]
    report: Dict[str, Any]
    history: Dict[str, Any]

    intent: str
    escalation: Dict[str, Any]
    final_answer: str
    response_payload: Dict[str, Any]

    errors: List[str]
    warnings: List[str]