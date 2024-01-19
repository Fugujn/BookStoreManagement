from sqlalchemy import func, desc

from MainApp import db, app
from MainApp.models import Configuration, ImportTicket, Book, Category, Author, PaymentMethod, User, Order, \
    OrderDetails


def get_configuration():
    return Configuration.query.first()


def save_ticket(url):
    ticket = ImportTicket(excel_url=url)
    db.session.add(ticket)
    db.session.commit()
    return ticket


def load_cate():
    return Category.query.all()


def load_book(cate_id=None, page=None, kw=None):
    books = Book.query.filter(Book.enable.__eq__(True))

    if kw:
        books = books.filter(Book.name.contains(kw))

    if cate_id:
        books = books.filter(Book.category_id.__eq__(cate_id))

    if page:
        page = int(page)
        page_size = app.config['PAGE_SIZE']
        start = (page - 1) * page_size

        return books.slice(start, start + page_size)

    return books.all()


def get_book_by_name(name):
    return Book.query.filter(Book.name.__eq__(name)).first()


def save_book(book):
    db.session.add(book)
    db.session.commit()


def get_category_by_name(name):
    return Category.query.filter(Category.name.__eq__(name)).first()


def save_category(category):
    db.session.add(category)
    db.session.commit()


def get_author_by_name(name):
    return Author.query.filter(Author.name.__eq__(name)).first()


def save_author(author):
    db.session.add(author)
    db.session.commit()


def save_ticket_details(ticket_details):
    db.session.add(ticket_details)
    db.session.commit()


def get_payment_method_by_id(id):
    return PaymentMethod.query.get(id)


def get_payment_method_all():
    return PaymentMethod.query.all()


def get_user_by_id(id):
    return User.query.get(id)


def save_user(user):
    db.session.add(user)
    db.session.commit()


def get_user_by_phone(phone):
    return User.query.filter(User.phone_number.__eq__(phone)).first()


def get_user_by_username(username):
    return User.query.filter(User.username.__eq__(username)).first()


def get_book_by_id(id):
    return Book.query.get(id)


def save_order(order):
    db.session.add(order)
    db.session.commit()


def save_order_details(order_detail):
    db.session.add(order_detail)
    db.session.commit()


def get_order_by_id(order_id):
    return Order.query.get(order_id)


def get_orders_by_customer_id(customer_id):
    return Order.query.filter_by(customer_id=customer_id).order_by(Order.id.asc()).all()


def stat_book_by_month(month):
    return db.session.query(Book.name, Category.name, func.sum(OrderDetails.quantity).label("quantity")) \
        .join(Book, Book.id == OrderDetails.book_id) \
        .join(Order, OrderDetails.order_id == Order.id) \
        .join(Category, Book.category_id == Category.id) \
        .group_by(Book.name) \
        .filter(func.extract("month", Order.paid_date) == month) \
        .order_by(desc("quantity")) \
        .all()


def stat_category_by_month(month):
    return db.session.query(Category.name, func.count(OrderDetails.book_id),
                            func.sum(OrderDetails.quantity * OrderDetails.unit_price).label("revenue")) \
        .join(Book, Category.id == Book.category_id) \
        .join(OrderDetails, Book.id == OrderDetails.book_id) \
        .join(Order, OrderDetails.order_id == Order.id) \
        .group_by(Category.name) \
        .filter(func.extract("month", Order.paid_date) == month) \
        .order_by(desc("revenue")) \
        .all()


def statistic_revenue():
    return db.session.query(func.sum(Order.total_payment).label("revenue")) \
        .group_by(func.extract("month", Order.paid_date)) \
        .order_by(desc("revenue")) \
        .all()


def count_user():
    return User.query.count()
