from flask import url_for
from flask_admin import helpers as admin_helpers, Admin

from MainApp import app, db, security
from MainApp.models import User, Role, Book, Order, Configuration
from MainApp.views import MyAdminIndexView, StatsView, UserAdmin, RoleAdmin, ProductView, OrderView, BookImportView, \
    ConfigurationView

# Create admin
admin = Admin(
    app,
    'Bookstore',
    base_template='my_master.html',
    template_mode='bootstrap4',
    index_view=MyAdminIndexView()
)

# Thêm model views
admin.add_view(RoleAdmin(Role, db.session))
admin.add_view(UserAdmin(User, db.session))
admin.add_view(ProductView(Book, db.session))
admin.add_view(OrderView(Order, db.session))
admin.add_view(StatsView(name='Statistics'))
admin.add_view(BookImportView(name='Import Book'))
admin.add_view(ConfigurationView(Configuration, db.session))


@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )
