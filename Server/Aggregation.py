class ModelAggregationHandler:
    models = []
    scores = []

    def __init__(self, models_and_scores):
        self.models, self.scores = zip(*models_and_scores)

    def aggregate_models(self):
        try:
            index_min = min(range(len(self.scores)), key=self.scores.__getitem__)
        except ValueError:
            return None

        return self.models[index_min]

