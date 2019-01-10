import os
from pathlib import Path

import tensorflow as tf
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import pandas as pd
from dotenv import load_dotenv

from tensorflow.python.keras.callbacks import Callback

from sacred import Experiment
from sacred.observers import MongoObserver


class MetricsLogger(Callback):
    """Callback to log loss and accuracy to sacred database."""

    def __init__(self, run):
        super().__init__()
        self._run = run

    def on_epoch_end(self, epoch, logs):
        print("LOGS ARE:", logs)
        self._run.log_scalar("training_loss", float(logs['loss']), step=epoch)
        self._run.log_scalar("training_acc", float(logs['acc']), step=epoch)


def plot_confusion_matrix(confusion_matrix, class_names, figsize=(15, 12), fontsize=14):
    """Prints a confusion matrix, as returned by sklearn.metrics.confusion_matrix, as a heatmap.

    Based on https://gist.github.com/shaypal5/94c53d765083101efc0240d776a23823

    Arguments
    ---------
    confusion_matrix: numpy.ndarray
        The numpy.ndarray object returned from a call to sklearn.metrics.confusion_matrix.
        Similarly constructed ndarrays can also be used.
    class_names: list
        An ordered list of class names, in the order they index the given confusion matrix.
    figsize: tuple
        A 2-long tuple, the first value determining the horizontal size of the ouputted figure,
        the second determining the vertical size. Defaults to (10,7).
    fontsize: int
        Font size for axes labels. Defaults to 14.

    Returns
    -------
    matplotlib.figure.Figure
        The resulting confusion matrix figure
    """
    df_cm = pd.DataFrame(
        confusion_matrix, index=class_names, columns=class_names,
    )
    fig, ax = plt.subplots(figsize=figsize)
    heatmap = sns.heatmap(df_cm, annot=False, cmap="Blues")
    heatmap.set(ylabel='True label', xlabel='Predicted label')

    return fig


ex = Experiment('example')

is_travis = 'TRAVIS' in os.environ
if is_travis:
    mongo_uri = None
else:
    env_path = Path('..') / 'infrastructure' / 'sacred_setup' / '.env'
    load_dotenv(dotenv_path=env_path)
    mongo_uri = (f'mongodb://{os.environ["MONGO_INITDB_ROOT_USERNAME"]}:'
                 f'{os.environ["MONGO_INITDB_ROOT_PASSWORD"]}@localhost:27017/?authMechanism=SCRAM-SHA-1')

ex.observers.append(MongoObserver.create(
    url=mongo_uri,
    db_name='incense_test'))


@ex.config
def hyperparameters():
    optimizer = 'sgd'
    epochs = 1


def make_model():
    model = tf.keras.models.Sequential([
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(512, activation=tf.nn.relu),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(10, activation=tf.nn.softmax)
    ])
    return model


@ex.command
def conduct(epochs, optimizer, _run):
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
    x_train = x_train / 255.0
    x_test = x_test / 255.0

    model = make_model()

    model.compile(
        loss='sparse_categorical_crossentropy',
        optimizer=optimizer,
        metrics=['accuracy'],
    )

    metrics_logger = MetricsLogger(_run)

    model.fit(x_train, y_train,
              epochs=epochs,
              callbacks=[metrics_logger])

    predictions = model.predict(x_test)

    predictions = predictions.argmax(axis=1)
    predictions_df = pd.DataFrame({'predictions': predictions,
                                   'targets': y_test})
    predictions_df.to_pickle('predictions_df.pickle')
    _run.add_artifact('predictions_df.pickle', name='predictions_df')

    predictions_df.to_csv('predictions.csv', index=False)
    _run.add_artifact('predictions.csv', name='predictions')

    fig = plot_confusion_matrix(confusion_matrix(y_test, predictions),
                                class_names=list(range(10)))
    fig.savefig('confusion_matrix.png')
    _run.add_artifact('confusion_matrix.png', name='confusion_matrix')

    scalar_results = model.evaluate(x_test, y_test)

    results = dict(zip(model.metrics_names, scalar_results))
    print('Final test results')
    print(results)
    for metric, value in results.items():
        _run.log_scalar(f'test_{metric}', value)


if __name__ == '__main__':
    ex.run('conduct')
    ex.run('conduct', config_updates={'epochs': 3})
    ex.run('conduct', config_updates={'optimizer': 'adam'})
