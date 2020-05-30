from task.celery import app


class JobTest:

    name = ''
    id = ''
    age = 0

    def __init__(self, id, name, age ) -> None:
        super().__init__()
        self.id = id
        self.name = name
        self.age = age

    @app.task
    def add(self):
        return self.age + 1231;
