class QueryError(Exception):
    def __init__(self, model, *args, **query_args):
        super().__init__(*args)
        self.model = model
        self.query_args = query_args

    def __repr__(self):
        return f"Query Error: model {self.model}, args {self.query_args}"
