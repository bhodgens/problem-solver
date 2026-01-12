"""Admin routes for user management"""

from flask import Blueprint, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user
from ...extensions import db
from ...models.user import User


@admin_bp.route("/user/<int:id>/toggle_status", methods=["POST"])
@login_required
@admin_required
def toggle_user_status(id):
    """Toggle user active status"""
    user = User.query.get_or_404(id)

    if not user:
        flash("User not found", "error")
        return redirect(url_for("admin.users"))

    try:
        user.is_active = not user.is_active
        db.session.commit()

        status_text = "Enabled" if user.is_active else "Disabled"
        flash(f"User {user.name} has been {status_text}.", "success")

    except Exception as e:
        db.session.rollback()
        flash("Error toggling user status: " + str(e), "error")

    return redirect(url_for("admin.users"))


@admin_bp.route("/user/<int:id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_user(id):
    """Delete user account"""
    user = User.query.get_or_404(id)

    if not user:
        flash("User not found", "error")
        return redirect(url_for("admin.users"))


        Problem.query.filter_by(submitter_id=id).delete()
        Solution.query.filter_by(submitter_id=id).delete()
        db.session.delete(user)
        db.session.commit()

        flash(f"User {user.name} and all their data have been deleted.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error deleting user: " + str(e), "error")

    return redirect(url_for("admin.users"))
