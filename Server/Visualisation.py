import matplotlib.pyplot as plt


class Visualiser:
    @staticmethod
    def plot_history_over_epochs(histories, epochs):
        for history, ID in histories:
            plt.figure(figsize=(5, 5))
            loss = history.history['loss']
            val_loss = history.history['val_loss']
            epochs_range = range(epochs)

            plt.plot(epochs_range, loss, label='Training Data Loss')
            plt.plot(epochs_range, val_loss, label='Validation Data Loss')
            plt.legend(loc='lower left')
            plt.title(f'Loss over epochs for node id {ID}')
            plt.show()

    @staticmethod
    def plot_evaluation_losses(losses):
        pass

