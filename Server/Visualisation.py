import matplotlib.pyplot as plt


class Visualiser:
    @staticmethod
    def plot_history_over_epochs(histories, epochs):
        plt.style.use('ggplot')
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
    def plot_evaluation_losses(history_with_ids):
        plt.style.use('ggplot')
        plt.figure(figsize=(5, 5))

        val_losses = []
        ids = []
        for history, ID in history_with_ids:
            val_losses.append(history.history['val_loss'][-1])
            ids.append(ID)

        x_names = [i for i, _ in enumerate(ids)]
        plt.bar(x_names, val_losses, color='green')
        plt.xlabel("Validation loss")
        plt.ylabel("Node ID")
        plt.title("Losses for each ID")
        plt.xticks(x_names, ids)
        plt.show()
