class Evaluation(object):
    """
    Represents an Evaluation object
    """
    def __init__(self, eval_id, name, application_id, dataset_collection_id, start_time, description=None):
        self.id = eval_id
        self.name = name
        self.application_id = application_id
        self.dataset_collection_id = dataset_collection_id
        self.start_time = start_time
        self.description = description

    def __str__(self):
        return "Evaluation: id={}, name={}, application_id={}, dataset_collection_id={}, description={}, start_time={}".format(
            self.id, self.name, self.application_id, self.dataset_collection_id, self.description, self.start_time
        )

    def __repr__(self):
        return str(self)


class Run(object):
    """ Represents a run object """
    def __init__(self, run_id, evaluation_id, run_number, creation_time, completion_time=None, metadata=None):
        self.id = run_id
        self.evaluation_id = evaluation_id
        self.run_number = run_number
        self.creation_time = creation_time
        self.completion_time = completion_time
        self.metadata = metadata

    def __str__(self):
        return "Run: id={}, evaluation_id={}, run_number={}, creation_time={}, completion_time={}, metadata={}".format(
            self.id, self.evaluation_id, self.run_number, self.creation_time, self.completion_time, self.metadata
        )

    def __repr__(self):
        return str(self)

