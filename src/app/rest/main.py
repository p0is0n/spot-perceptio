from di.container import Container
from app.rest.base import create_app

app = create_app()

container = Container()
container.setup(app=app)
