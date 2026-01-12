"""Authentication blueprint with Google OAuth integration"""

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    session,
    flash,
    request,
    current_app,
)
from flask_login import login_user, logout_user, login_required, current_user
from authlib.integrations.flask_client import OAuth
from ...extensions import oauth, db
from ...models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login")
def login():
    """Handle Google OAuth login"""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    google = oauth.create_client("google")
    redirect_uri = url_for("auth.authorize", _external=True)
    return google.authorize_redirect(redirect_uri)


@auth_bp.route("/authorize")
def authorize():
    """Handle Google OAuth callback"""
    google = oauth.create_client("google")
    try:
        token = google.authorize_access_token()
        user_info = google.parse_id_token(token)

        user = User.query.filter_by(email=user_info["email"]).first()
        if not user:
            user = User(
                email=user_info["email"],
                name=user_info.get("name", ""),
                avatar_url=user_info.get("picture", ""),
                email_verified=user_info.get("email_verified", False),
                pseudonym_seed=user_info["email"],
            )
            db.session.add(user)
            db.session.commit()

        user.last_login = datetime.utcnow()
        user.email_verified = user_info.get("email_verified", False)
        db.session.commit()

        login_user(user, remember=True)
        flash("Successfully logged in!", "success")

        return redirect(url_for("main.index"))

    except Exception as e:
        current_app.logger.error(f"OAuth error: {str(e)}")
        flash("Login failed. Please try again.", "error")
        return redirect(url_for("auth.login"))


@auth_bp.route("/logout")
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/profile")
@login_required
def profile():
    """User profile page"""
    if request.method == "POST":
        current_user.name = request.form.get("name")
        current_user.visibility_preference = request.form.get(
            "visibility", "identified"
        )
        db.session.commit()
        flash("Profile updated!", "success")
        return redirect(url_for("auth.profile"))

    return render_template("auth/profile.html", user=current_user)


@auth_bp.route("/visibility/<preference>")
@login_required
def set_visibility(preference):
    """Set user visibility preference"""
    if preference in ["anonymous", "semi-anonymous", "identified"]:
        session["visibility_preference"] = preference
        flash(f"Visibility set to {preference}", "success")
    else:
        flash("Invalid visibility preference", "error")

    return redirect(request.referrer or url_for("main.index"))
