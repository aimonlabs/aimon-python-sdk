class MLModel(object):
    def __init__(self, company_id, name, type, description, metadata):
        self.company_id = company_id
        self.name = name
        self.type = type
        self.description = description
        self.metadata = metadata

    def __str__(self):
        return f"MLModel(company_id={self.company_id}, name={self.name}, type={self.type}, description={self.description}, metadata={self.metadata})"

    def __repr__(self):
        return self.__str__()


class Application(object):

    def __init__(self, app_id, company_id, name, model_id, stage, app_type, user_id, version, metadata):
        self.app_id = app_id
        self.company_id = company_id
        self.name = name
        self.model_id = model_id
        self.stage = stage
        self.type = app_type
        self.user_id = user_id
        self.version = version
        self.metadata = metadata

    def __str__(self):
        return f"Application(app_id={self.app_id}, company_id={self.company_id}, name={self.name}, model_id={self.model_id}, stage={self.stage}, type={self.type}, user_id={self.user_id}, version={self.version}, metadata={self.metadata})"

    def __repr__(self):
        return self.__str__()
