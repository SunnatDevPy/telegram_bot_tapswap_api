import os

import uvicorn
from libcloud.storage.drivers.local import LocalStorageDriver
from sqlalchemy_file.storage import StorageManager
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin.contrib.sqla import Admin, ModelView

from config import conf
from db import User, Phone, About, database, Network
from web.provider import UsernameAndPasswordProvider

middleware = [
    Middleware(SessionMiddleware, secret_key='1234')
]

app = Starlette(middleware=middleware)

admin = Admin(
    engine=database._engine,
    title="Translate Web site",
    base_url='/',
    auth_provider=UsernameAndPasswordProvider()
)


class ProductModelView(ModelView):
    exclude_fields_from_list = ('created_at', 'updated_at')
    exclude_fields_from_create = ('created_at', 'updated_at')
    exclude_fields_from_edit = ('created_at', 'updated_at')


class UserModelView(ModelView):
    exclude_fields_from_edit = ('created_at', 'updated_at')


class CategoryModelView(ModelView):
    exclude_fields_from_create = ('created_at', 'updated_at')
    exclude_fields_from_edit = ('created_at', 'updated_at')


class OrdersModelView(ModelView):
    exclude_fields_from_create = ('created_at', 'updated_at')
    exclude_fields_from_edit = ('created_at', 'updated_at')


# class HistoryModelView(ModelView):
#     exclude_fields_from_create = ('created_at', 'updated_at')
#     exclude_fields_from_edit = ('created_at', 'updated_at')


admin.add_view(UserModelView(User))
admin.add_view(CategoryModelView(Phone))
admin.add_view(ProductModelView(Network))
admin.add_view(ModelView(About))

# Mount admin to your app
admin.mount_to(app)

# Configure Storage
os.makedirs("./media/attachment", 0o777, exist_ok=True)
container = LocalStorageDriver("./media").get_container("attachment")
StorageManager.add_storage("default", container)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)
