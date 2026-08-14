from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_review_brief_is_evidence_driven_and_preserves_boundaries():
    page = (ROOT / "research-portal/app/professor-review/page.tsx").read_text(encoding="utf-8")
    assert "getPipeline" in page and "getProjectStatus" in page
    assert "BLOCKED_HARDWARE" in page and "HardwareStatus" in page
    assert "unsupported" in page.lower()
    assert "progress percentage" in page
    assert "14R" in page


def test_configuration_state_is_not_a_scientific_evidence_status():
    types = (ROOT / "research-portal/lib/types.ts").read_text(encoding="utf-8")
    collaboration = (ROOT / "research-portal/lib/collaboration.ts").read_text(encoding="utf-8")
    route = (ROOT / "research-portal/app/api/professor-review/route.ts").read_text(encoding="utf-8")
    assert "BLOCKED_CONFIGURATION" not in types
    assert '"BLOCKED_CONFIGURATION"' in collaboration
    assert "COLLABORATION_NOT_CONFIGURED" in route and "status: 503" in route
    assert "COLLABORATION_FEATURE_STATE" in collaboration


def test_collaboration_schema_has_private_storage_and_role_boundaries():
    migration = (ROOT / "supabase/migrations/20260814_professor_review_collaboration.sql").read_text(encoding="utf-8")
    for table in ("review_profiles", "review_invites", "review_documents", "discussion_threads", "discussion_comments", "moderation_log"):
        assert f"create table public.{table}" in migration
        assert f"alter table public.{table} enable row level security" in migration
    assert "PUBLIC_READER" in migration and "MODERATOR" in migration and "ADMIN" in migration
    assert "Only one reply level is permitted" in migration
    assert "public, file_size_limit" in migration and "public = false" in migration
    assert "reviewer uploads to own prefix" in migration
    assert "staff reads moderation log" in migration


def test_setup_docs_cover_safe_fallback_and_deployment_controls():
    setup = (ROOT / "docs/PROFESSOR_REVIEW_COLLABORATION_SETUP.md").read_text(encoding="utf-8")
    env = (ROOT / ".env.example").read_text(encoding="utf-8")
    catalog = (ROOT / "docs/PUBLIC_API_INTEGRATION_ASSESSMENT.md").read_text(encoding="utf-8")
    assert "BLOCKED_CONFIGURATION" in setup and "RLS" in setup and "malware" in setup.lower()
    assert "Vercel" in setup and "retention" in setup.lower()
    assert "COLLABORATION_FEATURE_STATE=disabled" in env
    assert "defer all integrations" in catalog.lower() and "GitHub REST API" in catalog


def test_meeting_documents_are_substantive():
    for name in ("PROFESSOR_REVIEW_BRIEF.md", "ADVISOR_MEETING_TALK.md"):
        words = (ROOT / "docs" / name).read_text(encoding="utf-8").split()
        assert 250 <= len(words) <= 380
