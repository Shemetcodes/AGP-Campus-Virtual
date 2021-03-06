from flask import flash, redirect, request, render_template, url_for
from flask_login import current_user, login_user, logout_user, login_required, fresh_login_required

from app import Msg
from . import auth
from .forms import LoginForm, RegisterForm, ChangePasswordForm, PasswordResetRequestForm, PasswordResetForm
from ..models import User, generate_password_hash
from ..email import send_email

@auth.route("/login",methods=["GET", "POST"])
def login():

    # User is already logged in
    if not current_user.is_anonymous:
        flash(Msg.Flash.ALREADY_LOGGED_IN)
        return redirect(url_for("main.index"))

    form = LoginForm()

    
    if form.validate_on_submit():
        user = User.get_user(email=form.email.data)
        if user is None:
            print("[DEBUG] User not found: {}".format(form.email.data))
            flash(Msg.Flash.INVALID_CREDENTIALS)
            return redirect(url_for("auth.login"))
    
        # Redirect user the page he or she was about to enter, but got asked to verify credentials.
        next = request.args.get("next")
        if next is None or not next.startswith('/'):
            next = url_for("main.index")        
    
        if not user.check_password(form.password.data):
            print("[DEBUG] Invalid user credentials: {} {}".format(form.email.data, form.password.data))
            flash(Msg.Flash.INVALID_CREDENTIALS)
            return redirect(url_for("auth.login", next=next))

        login_user(user, remember=form.remember_me.data)
        print("[DEBUG] Login from user: {} {}".format(user.email, user.first_name))
        

        return redirect(next)
    
    return render_template("auth/login.html", title="Iniciar sesión", form=form)

@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.get_user(form.email.data) is not None:
            print("[DEBUG] User with email {} already registered.".format(form.email.data))
            flash(Msg.UserRegistration.ERROR_EMAIL_IN_USE)
            return redirect(url_for("auth.register"))

        new_user = User.create_new_user(email=form.email.data, 
            first_name=form.first_name.data, 
            paternal_last_name=form.paternal_last_name.data, 
            maternal_last_name=form.maternal_last_name.data,
            birth_date=form.birth_date.data,
            gender=form.gender.data,
            occupation=form.occupation.data,
            password=form.password.data)

        print("[DEBUG] New user created. Showing JSON:")
        print(new_user.to_json())
        print("[DEBUG] New user EOF.")
        new_user.save()

        login_user(new_user, remember=False)
        flash(Msg.Flash.NEW_USER.format(first_name=new_user.first_name))
        return redirect(url_for("main.index"))
    
    return render_template("auth/register.html", title="Registrarse", form=form)

@auth.route("/logout")
def logout():
    if not current_user.is_anonymous:
        logout_user()
        flash(Msg.Flash.LOGOUT_USER)
    return redirect(url_for("main.index"))


@auth.route("/change-password", methods=["GET", "POST"])
@fresh_login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        
        # Check the old password
        if current_user.check_password(form.old_password.data):
        
            # Check that new password is not the same as the old one
            if form.old_password.data == form.password.data:
                flash(Msg.Flash.SAME_AS_OLD_PASSWORD)
                print("[DEBUG] User {} tried to change to same password.".format(current_user.email))
                return redirect(url_for("auth.change_password"))

        else:
            flash(Msg.Flash.INVALID_OLD_PASSWORD)
            print("[DEBUG] Password change request, incorrect old password. User: {}".format(current_user.email))
            return redirect(url_for("auth.change_password"))

        
        # Check that the user curently signed in is still on the database
        user = User.get_user(email=current_user.email)
        if user is None:
            print("[DEBUG] Password change request, user not found: {}".format(current_user.email))
            return redirect(url_for("error.not_found"))

        # No errors, proceed to commit changes to database
        user.password_hash = generate_password_hash(form.password.data)
        user.save()
        print("[DEBUG] Password change from user {}.".format(user.email))
        flash(Msg.Flash.PASSWORD_CHANGE_SUCCESFUL)
        return redirect(url_for("main.index"))
    return render_template("auth/change_password.html", form=form)



# View to request a password change, arrived at through "forgot password?"
# Redirects to index if user is NOT anonymous
@auth.route("/reset", methods=["GET", "POST"])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))

    form = PasswordResetRequestForm()
    if form.validate_on_submit():

        user = User.get_user(form.email.data)
        if user:
            token = user.generate_reset_token()
            send_email(user.email, Msg.Mail.RESET_PASSWORD_SUBJECT, "auth/email/reset_password",
                user=user, token=token)
        flash(Msg.Flash.PASSWORD_RESET_EMAIL_SENT)
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html", form=form)


# View to change reset password after token sent to email is validated.
# Redirects to index if user is NOT anonymous
@auth.route("/reset/<token>", methods=["GET", "POST"])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))
    
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            flash(Msg.Flash.PASSWORD_CHANGE_SUCCESFUL)
            return redirect(url_for("auth.login"))
        else:
            return redirect(url_for("main.index"))
    return render_template("auth/reset_password.html", form=form)