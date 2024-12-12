from app.do.resource import ResourceDO


class BaseRunner:
    def __init__(self, resource: ResourceDO):
        self.resource = resource

    def run(self):
        pass
