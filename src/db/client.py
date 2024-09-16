class DbClient:
    def __init__(self) -> None:
        pass

    def batch_write_db(self, model, model_items):
        with model.batch_write() as batch:
            for item in model_items:
                batch.save(item)

    def query_with_pk(self, model, pk):
        res = []
        for item in model.query(pk):
            res.append(item)
        return res
