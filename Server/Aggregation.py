import copy
import logging

import numpy as np


class ModelAggregationHandler:
    models = []
    scores = []

    def __init__(self, models_and_scores):
        self.models, self.scores = zip(*models_and_scores)

    def aggregate_models(self):
        logging.info(f"Beginning model aggregation with {len(self.models)} models")
        output = list(copy.deepcopy(self.models))

        # We have to have an even amount of models
        if len(output) % 2 == 1:
            output.append(output[-1])

        # Average models in pairs, like a pyramid to create the average of all the models at the top
        while len(output) > 1:
            it = iter(output)
            completed_models = []
            for model in it:
                new_model = self.average_two_models(model, next(it))
                completed_models.append(new_model)
            output = completed_models

        logging.info("Model aggregation complete")
        return output[0]

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
