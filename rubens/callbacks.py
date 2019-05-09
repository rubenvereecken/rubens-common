import numpy as np
import time
from typing import *

from collections import deque

from .report import CSVReporter

import logging; logger = logging.getLogger().getChild(__name__)


class Callback:
    """
    Abstract base class used to build new callbacks.

    Careful, if you define e.g. both on_step_start and on_batch_start,
    both will be called.
    """

    def __init__(self):
        # TODO check for suspicious misnamed methods
        pass

    def set_trainer(self, trainer):
        self.trainer = trainer

    def on_step_end(self, step, logs=None):
        pass

    def on_step_start(self, episode, step, logs=None):
        pass

    def on_episode_start(self, episode, logs=None):
        pass

    def on_episode_end(self, episode, logs=None):
        pass

    def on_train_start(self, logs=None):
        pass

    def on_train_end(self, logs=None):
        pass

    # Different experiments will have different lingo, structure's the same
    on_batch_start = on_step_start
    on_batch_end = on_batch_start
    on_epoch_start = on_episode_start
    on_epoch_end = on_episode_end


class WriteEpisodeStats(Callback):
    def __init__(self, name, fields):
        self.name = name
        # First field is going to be episode, should not be in here
        self.fields = fields
        self.reporter = CSVReporter(name, ['episode', *self.fields])

    def on_episode_end(self, episode, logs):
        self.reporter.writerow(episode, *[logs.get(field) for field in self.fields])


class AfterEveryEpisode(Callback):
    def __init__(self, callback):
        self.callback = callback

    def on_episode_end(self, episode, logs):
        self.callback(episode, logs)


class UponFinalEpisode(Callback):
    # Kinda lame but this is a way to get access to logs enrichers
    def __init__(self, callback: Callable[[Dict], None]):
        self.after_remarkable_episode = callback

    def on_train_end(self, logs):
        self.after_remarkable_episode(logs)


class EpisodeTimer(Callback):
    # Currently unused
    def on_episode_start(self, episode, logs):
        self.episode_start_t = time.time()

    def on_episode_end(self, episode, logs):
        episode_t = time.time() - self.episode_start_t


class TrainTimer(Callback):
    def on_train_start(self, logs):
        self.train_start_t = time.time()

    def on_train_end(self, logs):
        total_train_t = time.time() - self.train_start_t
        logger.debug('Finished training in {:.2f}s'.format(total_train_t))


class EarlyStopping(Callback):
    """
    Early Stopping to terminate training early under certain conditions
    """

    def __init__(self,
                 monitor='val_loss',
                 min_delta=0,
                 patience=5,
                 descent=True):
        """
        Arguments
        ---------
        monitor : string in {'val_loss', 'train_loss'}
            whether to monitor train or val loss
        min_delta : float
            minimum change in monitored value to qualify as improvement.
            This number should be positive.
        patience : integer
            number of epochs to wait for improvment before terminating.
            the counter be reset after each improvment
        """
        self.monitor = monitor
        self.min_delta = min_delta
        self.patience = patience
        self.descent = descent

        # Keep track
        self.wait = 0
        self.best_loss = None # Make sure you on_train_start
        self.stopped_epoch = None
        super(EarlyStopping, self).__init__()


    def on_train_start(self, logs=None):
        self.wait = 0
        self.best_loss = 1e15 if self.descent else -1e15

    def on_epoch_end(self, epoch, logs: Dict):
        current_loss = logs.get(self.monitor)
        assert current_loss is not None

        # Beaten the best so far
        if self.descent and (self.best_loss - current_loss) > self.min_delta:
            self.best_loss = current_loss
            self.wait = 1
        elif self.descent is False and (current_loss - self.best_loss) > self.min_delta:
            self.best_loss = current_loss
            self.wait = 1
        # Start waiting patiently
        else:
            if self.wait >= self.patience:
                self.stopped_epoch = epoch
                self.trainer.stop_training()
            self.wait += 1

    def on_train_end(self, logs=None):
        if self.stopped_epoch > 0:
            logger.info('Terminated training by Early Stopping at epoch {:04d}'.format(self.stopped_epoch))


class AbsoluteEarlyStopping(Callback):
    def __init__(self, limit, monitor='train_loss', descent=True):
        self.monitor = monitor
        self.descent = descent
        self.limit = limit

        self.last_loss = None
        self.stopped_epoch = None

    def on_train_start(self, logs):
        self.last_loss = 1e15 if self.descent else -1e15

    def on_epoch_end(self, epoch, logs):
        current_loss = logs.get(self.monitor)
        assert current_loss is not None

        if self.descent and current_loss <= self.limit or \
           self.descent is False and current_loss >= self.limit:
            self.stopped_epoch = epoch
            self.trainer.stop_training()

        self.last_loss = current_loss

    def on_train_end(self, logs=None):
        if self.stopped_epoch > 0:
            logger.info('Terminated training early (limit {:.3f}) at epoch {:d}'.format(
                self.limit, self.stopped_epoch))


class CallbackManager:
    """
    Container holding a list of callbacks.
    """
    def __init__(self, trainer, callbacks=None, queue_length=10):
        self.callbacks = []
        self.trainer = trainer
        self.queue_length = queue_length

        for callback in callbacks or []:
            self.append(callback)

    def append(self, callback):
        callback.set_trainer(self.trainer)
        self.callbacks.append(callback)

    def set_params(self, params):
        for callback in self.callbacks:
            callback.set_params(params)

    def set_trainer(self, trainer):
        self.trainer = trainer
        for callback in self.callbacks:
            callback.set_trainer(trainer)

    def on_episode_start(self, episode, logs=None):
        logs = logs or {}
        for callback in self.callbacks:
            callback.on_episode_start(episode, logs)
            callback.on_epoch_start(episode, logs)

    def on_episode_end(self, episode, logs=None):
        logs = logs or {}
        for callback in self.callbacks:
            callback.on_episode_end(episode, logs)
            callback.on_epoch_end(episode, logs)

    def on_train_start(self, logs=None):
        logs = logs or {}
        # logs['start_time'] = _get_current_time()
        for callback in self.callbacks:
            callback.on_train_start(logs)

    def on_train_end(self, logs=None):
        logs = logs or {}
        # logs['final_loss'] = self.trainer.history.episode_losses[-1],
        # logs['best_loss'] = min(self.trainer.history.episode_losses),
        # logs['stop_time'] = _get_current_time()
        for callback in self.callbacks:
            callback.on_train_end(logs)

    def on_step_end(self, step, logs=None):
        for callback in self.callbacks:
            callback.on_step_end(step, logs)
            callback.on_batch_end(step, logs)

    def on_step_start(self, step, logs=None):
        for callback in self.callbacks:
            callback.on_step_start(step, logs)
            callback.on_batch_start(step, logs)

    # Different experiments will have different lingo, structure's the same
    on_batch_start = on_step_start
    on_batch_end = on_batch_start
    on_epoch_start = on_episode_start
    on_epoch_end = on_episode_end


# TODO this is definitely not perfect yet, it swaps out the managed instance
# Will definitely break with inheritance. Look at how I did Pretty class
class CallbackManaged:
    managed_methods = ['on_step_start', 'on_step_end', 'on_episode_start',
                       'on_episode_end', 'on_train_start', 'on_train_end']

    def __init__(self, cls, callback_manager_name='callback_manager'):
        self.managed_cls = cls
        self.manager_name = callback_manager_name
        self._setup_methods()

    def __call__(self, *args, **kwargs):
        instance = self.managed_cls(*args, **kwargs)
        return instance

    def _setup_methods(self):
        # I need method_name to be captured in this closure. Doing it inline
        # further down would result in method to take on the list's last value
        def _create_method(method_name):
            def _callback(that, *args):
                manager = getattr(that, self.manager_name)
                manager_method = getattr(manager, method_name)
                return manager_method(*args)
            return _callback

        for method in self.managed_methods:
            if hasattr(self.managed_cls, method):
                continue
            setattr(self.managed_cls, method, _create_method(method))

