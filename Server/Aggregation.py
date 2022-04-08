import copy
import logging

import numpy as np


class ModelAggregationHandler:
    """Handles the aggregation of client models into an average model"""
    models = []
    scores = []

    def __init__(self, models_and_scores):
        self.models, self.scores = zip(*models_and_scores)

    def aggregate_models(self):
        logging.info(f"Beginning model aggregation with {len(self.models)} models")
        # We don't want to alter the original models
        output = list(copy.deepcopy(self.models))

        # We have to have an even amount of models
        if len(output) % 2 == 1:
            output.append(output[-1])

        # Average models in pairs
        # Example:
        # Model1, Model2, Model3, Model4
        # model5=avg(Model1, Model2), model6=avg(Model3, Model4)
        # model7=avg(model5, model6)
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
        # Get 2D array of weights for the layers
        weights_model_1 = np.array(model_1.get_weights(), dtype=object)
        weights_model_2 = np.array(model_2.get_weights(), dtype=object)

        new_weights = []
        # New weights for each layer become the element-wise average of the two input layers
        for i in range(len(weights_model_1)):
            first_model_row = weights_model_1[i]
            second_model_row = weights_model_2[i]
            new_row = (first_model_row + second_model_row) / 2.0
            new_weights.append(new_row)

        new_model = copy.deepcopy(model_1)
        new_model.set_weights(new_weights)
        return new_model
