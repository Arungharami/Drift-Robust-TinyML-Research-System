import { CollaborationNotice } from "./CollaborationNotice";

export function ProfessorReviewTabs({ brief }: { brief: React.ReactNode }) {
  return <>
    <nav className="review-tabs" aria-label="Professor review workspace"><a href="#review-brief">Review Brief</a><a href="#shared-documents">Shared Documents</a><a href="#discussion">Discussion</a></nav>
    <section id="review-brief">{brief}</section>
    <section id="shared-documents" className="review-workspace"><h2>Shared documents</h2><p>Approved public documents will appear here after moderator review. Private submissions, storage paths, reviewer emails, and moderation notes are never public.</p><CollaborationNotice /></section>
    <section id="discussion" className="review-workspace"><h2>Discussion</h2><p>Published discussion will appear here. Reviewer comments represent contributor perspectives, not verified project findings; they become evidence only through the separate evidence pipeline.</p><CollaborationNotice /></section>
  </>;
}
