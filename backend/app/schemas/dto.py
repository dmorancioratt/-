from pydantic import BaseModel, Field


class JDParseRequest(BaseModel):
    text: str


class JobUpdateRequest(BaseModel):
    domain: str | None = None
    job_type: str | None = None
    level: str | None = None
    description: str | None = None
    status: str | None = None
    required_skills: list[str] | None = None
    preferred_skills: list[str] | None = None
    update_note: str = "人工优化岗位画像"
    evidence_sources: list[str] = Field(default_factory=list)


class ResumeParseRequest(BaseModel):
    text: str


class ResumeSnapshotRequest(BaseModel):
    resume: dict
    source_filename: str = "历史解析结果"
    raw_text: str = ""


class MatchAnalysisRequest(BaseModel):
    resume_id: int | None = None
    resume: dict | None = None
    use_profile: bool = False
    target_job_id: int | None = None
    target_job_name: str | None = None


class AIAnalyzeRequest(BaseModel):
    task_type: str
    payload: dict


class DigitalInterviewRequest(BaseModel):
    job_name: str
    resume_summary: str | None = None
    candidate_answer: str | None = None
    stage: str = "opening"
    interview_session_id: int | None = None
    interview_style: str = "adaptive"
    action: str = "answer"
    digital_human_session_id: str | None = None


class DigitalHumanSpeakRequest(BaseModel):
    session_id: str
    text: str


class DigitalHumanSessionRequest(BaseModel):
    session_id: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    confirm_password: str
    role: str = "candidate"
    display_name: str = ""
    email: str
    phone: str = ""
    organization: str = ""
    captcha_token: str
    captcha_answer: str


class LoginRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
    confirm_new_password: str = ""


class AccountUpdateRequest(BaseModel):
    display_name: str | None = None
    email: str | None = None
    phone: str | None = None
    organization: str | None = None


class CandidateProfileUpdateRequest(BaseModel):
    real_name: str = ""
    education: str = ""
    major: str = ""
    school: str = ""
    target_role: str = ""
    city: str = ""
    expected_salary: str = ""
    avatar_url: str = ""
    skills: list[str] = []
    certificates: list[str] = []
    projects: list[str] = []
    internships: list[str] = []
    awards: list[str] = []
    self_summary: str = ""


class ReviewActionResponse(BaseModel):
    id: int
    status: str
    message: str
