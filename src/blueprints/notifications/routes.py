"""Notifications blueprint for managing user alerts and preferences"""

from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from ...extensions import db
from ...utils.notification_manager import NotificationManager
from ...models.supporting import Notification

notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.route("/")
@login_required
def index():
    """Display user notifications"""
    page = request.args.get("page", 1, type=int)
    per_page = 20

    notifications_query = Notification.query.filter_by(user_id=current_user.id)
    notifications = notifications_query.order_by(
        Notification.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        "notifications/index.html", notifications=notifications, page=page
    )


@notifications_bp.route("/unread")
@login_required
def unread():
    """Get unread notifications as JSON"""
    unread_notifications = current_user.get_unread_notifications_count()

    return jsonify(
        {
            "count": len(unread_notifications),
            "notifications": [
                {
                    "id": notif.id,
                    "title": notif.title,
                    "message": notif.message,
                    "link": notif.link,
                    "created_at": notif.created_at.isoformat(),
                    "event_type": notif.event_type,
                }
                for notif in unread_notifications
            ],
        }
    )


@notifications_bp.route("/mark-read/<int:notification_id>", methods=["POST"])
@login_required
def mark_read(notification_id):
    """Mark notification as read"""
    if NotificationManager.mark_notification_read(notification_id, current_user.id):
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Notification not found"})


@notifications_bp.route("/mark-all-read", methods=["POST"])
@login_required
def mark_all_read():
    """Mark all notifications as read"""
    unread_notifications = Notification.query.filter_by(
        user_id=current_user.id, is_read=False
    ).all()

    for notification in unread_notifications:
        notification.is_read = True

    db.session.commit()

    return jsonify({"success": True, "count": len(unread_notifications)})


@notifications_bp.route("/preferences")
@login_required
def preferences():
    """Notification preferences management"""
    if request.method == "POST":
        email_notifications = request.form.get("email_notifications", "daily")
        digest_frequency = request.form.get("digest_frequency", "daily")
        notification_types = []

        if request.form.get("notify_problems"):
            notification_types.append("problems")
        if request.form.get("notify_solutions"):
            notification_types.append("solutions")
        if request.form.get("notify_evaluations"):
            notification_types.append("evaluations")
        if request.form.get("notify_votes"):
            notification_types.append("votes")
        if request.form.get("notify_comments"):
            notification_types.append("comments")

        # Update user preferences
        current_user.email_notifications = email_notifications
        current_user.digest_frequency = digest_frequency
        current_user.notification_types = (
            ",".join(notification_types) if notification_types else ""
        )
        db.session.commit()

        flash("Notification preferences updated!", "success")
        return redirect(url_for("notifications_bp.index"))

    return render_template("notifications/preferences.html")


@notifications_bp.route("/delete/<int:notification_id>", methods=["POST"])
@login_required
def delete_notification(notification_id):
    """Delete a notification"""
    notification = Notification.query.filter_by(
        id=notification_id, user_id=current_user.id
    ).first()

    if notification:
        db.session.delete(notification)
        db.session.commit()
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Notification not found"})
