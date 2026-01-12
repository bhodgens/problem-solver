"""
Notification utilities for user alerts and email digests
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from flask import current_app
from flask_mail import Message
from ..extensions import db, mail
from ..models.supporting import Notification, User
from ..models.problem import Problem
from ..models.solution import Solution
from ..models.evaluation import ProblemEvaluation, SolutionEvaluation


class NotificationManager:
    """Manages notification creation and delivery"""

    NOTIFICATION_TYPES = {
        "problem_created": "New Problem: {title}",
        "solution_added": "New Solution to: {problem_title}",
        "evaluation_received": "Evaluation Received for: {title}",
        "solution_voted": "Your solution was voted on",
        "comment_added": "New comment on: {title}",
        "problem_status_changed": "Problem Status Changed: {title}",
        "digest_daily": "Daily Digest - {count} new activities",
        "digest_weekly": "Weekly Digest - {count} new activities",
    }

    @staticmethod
    def create_notification(
        user_id: int,
        event_type: str,
        title: str,
        message: str,
        link: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Notification:
        """Create a notification record"""
        notification = Notification(
            user_id=user_id,
            event_type=event_type,
            title=title,
            message=message,
            link=link,
            payload=payload or {},
            is_read=False,
            created_at=datetime.utcnow(),
        )

        db.session.add(notification)
        return notification

    @staticmethod
    def notify_problem_created(problem: Problem) -> None:
        """Send notifications when a new problem is created"""
        # Notify admin users about new problem
        from ..models.user import User

        admin_users = User.query.filter_by(role="admin").all()

        for admin in admin_users:
            NotificationManager.create_notification(
                user_id=admin.id,
                event_type="problem_created",
                title=f"New Problem: {problem.title}",
                message=f'A new problem "{problem.title}" has been submitted for review.',
                link=f"/problems/{problem.id}",
                payload={"problem_id": problem.id},
            )

    @staticmethod
    def notify_solution_added(solution: Solution) -> None:
        """Send notifications when a solution is added"""
        # Notify problem submitter
        NotificationManager.create_notification(
            user_id=solution.problem.submitter_id,
            event_type="solution_added",
            title=f"New Solution to: {solution.problem.title}",
            message=f'A new solution has been added to your problem "{solution.problem.title}".',
            link=f"/solutions/{solution.id}",
            payload={"solution_id": solution.id, "problem_id": solution.problem.id},
        )

    @staticmethod
    def notify_evaluation_received(
        evaluation, problem_id: int = None, solution_id: int = None
    ) -> None:
        """Send notifications when an evaluation is received"""
        target_id = problem_id or solution_id
        target_type = "problem" if problem_id else "solution"

        # Get the content creator
        if problem_id:
            content = Problem.query.get(problem_id)
            if content:
                NotificationManager.create_notification(
                    user_id=content.submitter_id,
                    event_type="evaluation_received",
                    title=f"Evaluation Received for: {content.title}",
                    message=f'Your problem "{content.title}" has received a new evaluation.',
                    link=f"/problems/{content.id}",
                    payload={"evaluation_id": evaluation.id, "problem_id": problem_id},
                )

        elif solution_id:
            content = Solution.query.get(solution_id)
            if content:
                NotificationManager.create_notification(
                    user_id=content.submitter_id,
                    event_type="evaluation_received",
                    title=f"Evaluation Received for: {content.title}",
                    message=f"Your solution has received a new evaluation.",
                    link=f"/solutions/{content.id}",
                    payload={
                        "evaluation_id": evaluation.id,
                        "solution_id": solution_id,
                    },
                )

    @staticmethod
    def send_email_notification(
        user_email: str, user_name: str, subject: str, html_body: str, text_body: str
    ) -> bool:
        """Send email notification to user"""
        try:
            message = Message(
                subject=subject,
                sender=current_app.config["MAIL_DEFAULT_SENDER"],
                recipients=[user_email],
                html=html_body,
                body=text_body,
            )

            mail.send(message)
            return True

        except Exception as e:
            current_app.logger.error(f"Failed to send email to {user_email}: {str(e)}")
            return False

    @staticmethod
    def get_unread_notifications(user_id: int, limit: int = 20) -> List[Notification]:
        """Get unread notifications for a user"""
        return (
            Notification.query.filter_by(user_id=user_id, is_read=False)
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def mark_notification_read(notification_id: int, user_id: int) -> bool:
        """Mark a notification as read"""
        notification = Notification.query.filter_by(
            id=notification_id, user_id=user_id
        ).first()

        if notification:
            notification.is_read = True
            db.session.commit()
            return True

        return False

    @staticmethod
    def create_digest_email(
        user_email: str, user_name: str, notifications: List[Notification]
    ) -> Dict[str, str]:
        """Create email digest from multiple notifications"""
        if not notifications:
            return {
                "subject": "No new notifications",
                "html_body": "<p>You have no new notifications.</p>",
                "text_body": "You have no new notifications.",
            }

        # Group notifications by type for better organization
        grouped = {}
        for notification in notifications:
            event_type = notification.event_type
            if event_type not in grouped:
                grouped[event_type] = []
            grouped[event_type].append(notification)

        # Build HTML content
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h2 style="color: #333; margin-bottom: 20px;">Problem Solver Platform - Daily Digest</h2>
                <p style="color: #666; margin-bottom: 20px;">Hello {user_name},</p>
                <p style="color: #666; margin-bottom: 20px;">Here's what you missed:</p>
                
                {NotificationManager._build_digest_sections(grouped)}
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="color: #999; font-size: 12px;">
                    This is an automated notification from the Problem Solver Platform.<br>
                    You can adjust your notification preferences in your profile settings.
                </p>
            </div>
        </body>
        </html>
        """

        text_content = f"""
Problem Solver Platform - Daily Digest

Hello {user_name},

Here's what you missed:

{NotificationManager._build_text_digest(grouped)}

This is an automated notification from the Problem Solver Platform.
You can adjust your notification preferences in your profile settings.
        """

        return {
            "subject": f"Problem Solver Platform - Daily Digest ({len(notifications)} items)",
            "html_body": html_content,
            "text_body": text_content,
        }

    @staticmethod
    def _build_digest_sections(
        grouped_notifications: Dict[str, List[Notification]],
    ) -> str:
        """Build HTML sections for digest email"""
        sections = []

        for event_type, notifications in grouped_notifications.items():
            if event_type == "problem_created":
                section_html = '<h3 style="color: #007bff;">New Problems</h3><ul>'
                for notif in notifications:
                    section_html += f'<li><a href="{notif.link}" style="color: #007bff;">{notif.title}</a></li>'
                section_html += "</ul>"
                sections.append(section_html)

            elif event_type == "solution_added":
                section_html = '<h3 style="color: #28a745;">New Solutions</h3><ul>'
                for notif in notifications:
                    section_html += f'<li><a href="{notif.link}" style="color: #28a745;">{notif.title}</a></li>'
                section_html += "</ul>"
                sections.append(section_html)

            elif event_type == "evaluation_received":
                section_html = '<h3 style="color: #17a2b8;">New Evaluations</h3><ul>'
                for notif in notifications:
                    section_html += f'<li><a href="{notif.link}" style="color: #17a2b8;">{notif.title}</a></li>'
                section_html += "</ul>"
                sections.append(section_html)

        return "<br>".join(sections)

    @staticmethod
    def _build_text_digest(grouped_notifications: Dict[str, List[Notification]]) -> str:
        """Build text content for digest email"""
        sections = []

        for event_type, notifications in grouped_notifications.items():
            if event_type == "problem_created":
                section = f"New Problems:\n"
                for notif in notifications:
                    section += f"- {notif.title}\n"
                sections.append(section)

            elif event_type == "solution_added":
                section = f"New Solutions:\n"
                for notif in notifications:
                    section += f"- {notif.title}\n"
                sections.append(section)

            elif event_type == "evaluation_received":
                section = f"New Evaluations:\n"
                for notif in notifications:
                    section += f"- {notif.title}\n"
                sections.append(section)

        return "\n\n".join(sections)

    @staticmethod
    def send_digest_emails() -> int:
        """Send daily digest emails to users"""
        from ..models.user import User

        # Get users who want daily digests (would be a user preference field)
        # For now, send to all active users
        users = User.query.filter_by(is_active=True).all()

        sent_count = 0

        for user in users:
            # Get unread notifications from last 24 hours
            yesterday = datetime.utcnow() - timedelta(days=1)
            unread_notifications = Notification.query.filter(
                Notification.user_id == user.id,
                Notification.is_read == False,
                Notification.created_at >= yesterday,
            ).all()

            if unread_notifications:
                digest = NotificationManager.create_digest_email(
                    user.email, user.name or "User", unread_notifications
                )

                if NotificationManager.send_email_notification(
                    user.email,
                    user.name or "User",
                    digest["subject"],
                    digest["html_body"],
                    digest["text_body"],
                ):
                    # Mark notifications as sent
                    for notification in unread_notifications:
                        notification.email_sent = True
                    db.session.commit()
                    sent_count += 1

        return sent_count
