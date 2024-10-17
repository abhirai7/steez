from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from src.server import app, db
from src.server.models import __models__

admin = Admin(
    app, url="/admin", template_mode="bootstrap4", endpoint="sql", name=""
)


class AdminModelView(ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    can_delete = False
    can_export = True


for model in __models__:
    admin.add_view(AdminModelView(model, db.session))
