import datetime

from flask import Blueprint, request, render_template, redirect, url_for, flash, session, jsonify, abort
from flask_security import current_user, login_required

from MainApp import dao, utils
from MainApp.cart.utils import handle_cart
from MainApp.orders.forms import Checkout

orders = Blueprint('orders', __name__)


@orders.route("/orders")
@login_required
def orderBooks():
    orders = dao.get_orders_by_customer_id(current_user.id)
    return render_template('orderBooks.html', title='Order Books', orders=orders, datetime=datetime.datetime)


@orders.route("/order_details", methods=['GET'])
@login_required
def view_order_details():
    order_id = int(request.args.get("order_id"))
    products, grand_total, grand_total_plus_shipping, order_quantity_total, isPaid, isDelivered, isCanceled = utils.handle_order_details(
        order_id)
    return render_template("order_details.html", products=products, grand_total=grand_total,
                           grand_total_plus_shipping=grand_total_plus_shipping,
                           order_quantity_total=order_quantity_total)


@orders.route("/api/order_details")
@login_required
def get_order_details():
    order_id = int(request.args.get("order_id"))
    if order_id:
        products, grand_total, grand_total_plus_shipping, order_quantity_total, isPaid, isDelivered, isCanceled = utils.handle_order_details(
            order_id)
        return jsonify({
            "order_id": order_id,
            "products": products,
            "grand_total": grand_total,
            "grand_total_plus_shipping": grand_total_plus_shipping,
            "order_quantity_total": order_quantity_total,
            "isPaid": isPaid,
            "isDelivered": isDelivered,
            "isCanceled": isCanceled
        })
    else:
        abort(400)


@orders.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    configuration = dao.get_configuration()
    payment_methods = dao.get_payment_method_all()
    products, grand_total, grand_total_plus_shipping, quantity_total = handle_cart()
    form = Checkout()
    form.payment_type.choices = [(method.id, method.name) for method in payment_methods]
    if request.method == "GET":
        customer = None
        # in table order request
        if (request.args.get("staff_id") is not None) and (request.args.get("customer_phone")):
            if int(request.args.get("staff_id")) == current_user.id:
                customer_phone = request.args.get("customer_phone")
                if customer_phone:
                    customer = dao.get_user_by_phone(customer_phone)
                else:
                    customer = dao.get_user_by_username("user@example.com")

            else:
                flash("Can't create order", "danger")
                return redirect(url_for("users.staff"))
        # online
        else:
            customer = current_user
        form.customer_id.data = customer.id
        form.name.data = customer.name
        form.phone_number.data = customer.phone_number
        form.email.data = customer.email
        form.address.data = customer.address
    elif form.validate_on_submit():
        customer = None
        staff = None
        # in table order
        if int(form.customer_id.data) != current_user.id:
            customer = dao.get_user_by_id(int(form.customer_id.data))
            staff = current_user
        # online order
        else:
            customer = current_user
            # staff is the one who managed online order, has username = staff@example.com
            staff = dao.get_user_by_username("staff@example.com")
        order = utils.create_order(customer.id, staff.id, session['cart'], form.payment_type.data)
        session['cart'] = []
        session.modified = True

        if (current_user.id != customer.id):
            flash("New order has been created", "success")
            return redirect(url_for("users.staff"))
        else:
            if current_user.phone_number != form.phone_number.data or current_user.address != form.address.data:
                update_user = dao.get_user_by_id(current_user.id)
                update_user.phone_number = form.phone_number.data
                update_user.address = form.address.data
                dao.save_user(update_user)
            return redirect(url_for('orders.orderBooks'))

    return render_template('checkout.html', form=form, grand_total=grand_total,
                           grand_total_plus_shipping=grand_total_plus_shipping, quantity_total=quantity_total,
                           quick_ship=configuration.quick_ship)
