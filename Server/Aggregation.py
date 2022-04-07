import copy

import numpy as np


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

    @staticmethod
    def average_two_models(model_1, model_2):
        weights_model_1 = np.array(model_1.get_weights(), dtype=object)
        weights_model_2 = np.array(model_2.get_weights(), dtype=object)

        new_weights = []
        for i in range(len(weights_model_1)):
            first_model_row = weights_model_1[i]
            second_model_row = weights_model_2[i]
            new_row = (first_model_row + second_model_row) / 2.0
            new_weights.append(new_row)

        new_model = copy.deepcopy(model_1)
        new_model.set_weights(new_weights)
        return new_model
