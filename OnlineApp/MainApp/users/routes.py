from flask import render_template, request, Blueprint, url_for, redirect, flash, session, jsonify
from flask_security import logout_user, current_user, roles_accepted, login_required
from MainApp.users.forms import UpdateAccountForm, RegistrationForm, LoginForm
from MainApp.cart.forms import AddToCart
from MainApp.cart.utils import handle_cart
from MainApp.users.utils import save_picture, extract_search_user_by_phone

from MainApp import db, user_datastore, dao
from flask_security.utils import hash_password, verify_password, login_user

users = Blueprint('users', __name__)


@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = form.get_user()
        print("Register User: %s" % user)
        if not user:
            hashed_password = hash_password(form.password.data)
            new_user = user_datastore.create_user(
                username=form.name.data, email=form.email.data, password=hashed_password, active=False
            )
            db.session.commit()
            flash(f"Your account has been created! Please confirm your account by the code we sent to your email!",
                  "success")
            return redirect(url_for("users.verify", user_id=new_user.id))
    return render_template("register.html", title='Registration', form=form)


@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = LoginForm()

    if form.validate_on_submit():
        user = form.get_user()
        login_user(user, remember=form.remember.data)
        flash(f'You have been logged in!', 'success')
        # remember previous page is required and transferred to login
        if 'book_id' in request.args:
            return redirect(url_for(request.args.get('next', 'index'), book_id=request.args['book_id']))
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('main.home'))
    else:
        flash(f'Login Unsuccessful. Please check email and password', 'danger')
    return render_template("login.html", title='Login', form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/account', methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()

    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        if current_user.username != form.username.data \
                or form.picture.data \
                or current_user.name != form.name.data \
                or current_user.phone_number != form.phone.data:
            current_user.name = form.name.data
            current_user.phone_number = form.phone.data
            current_user.name = form.name.data
            db.session.commit()
            flash("Your account has been updated!", "success")
            return redirect(url_for("users.account"))


    elif request.method == "GET":
            form.process()
            form.name.data = current_user.name
            form.email.data = current_user.email
            form.phone.data = current_user.phone_number
            image_file = url_for('static', filename=f"profile_pics/{current_user.image_file}")
    return render_template("account.html", title='Account', image_file=image_file, form=form)


@users.route('/staff', methods=["GET", "POST"])
@login_required
@roles_accepted('staff', 'admin')
def staff():
    if "cart" not in session:
        session["cart"] = []
    form = AddToCart()

    id = form.id.data
    quantity = form.quantity.data
    print(id, quantity)
    if id is None and request.method == "POST":
        flash("Your Id book is Empty. Please input fill", "warning")

    if form.validate_on_submit() and id is not None and request.method == "POST":
        product = [prod for prod in session["cart"] if prod["id"] == int(id)]
        index = [index for index, prod in enumerate(session["cart"]) if prod["id"] == int(id)]
        if len(product) == 0:
            session["cart"].append({"id": id, "quantity": quantity})
        else:
            session["cart"][index[0]]['quantity'] = product[0]['quantity'] + quantity
        session.modified = True
    elif request.method == "GET":
        form.id.data = ""
        form.quantity.data = 1
    products, grand_total, grand_total_plus_shipping, quantity_total = handle_cart()
    return render_template("staff.html", title='Staff Action', form=form, products=products, grand_total=grand_total,
                           quantity_total=quantity_total)


@users.route("/api/user/search_by_phone", methods=["GET"])
@login_required
def process_search_user_by_phone():
    try:
        keyword = request.args.get("kw")
        max = int(request.args.get("max"))
        return jsonify(extract_search_user_by_phone(keyword, max))
    except:
        return jsonify([])
