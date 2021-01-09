from abc import ABCMeta, abstractmethod

from scripts.notificator import NotificationType

class BaseFormatter(metaclass=ABCMeta):

    @abstractmethod
    def to_text(self, fixture, linedelta):
        raise NotImplementedError


class TelegramFormatter(BaseFormatter):
    def to_text(self, fixture, linedelta):
        type_text_pattern = "NOTIFICATION TYPE - [{0}]."
        fixture_text = "*{0}* *{1}* - *{2}*.".format(fixture["tournament_name"],
                                             fixture["home_name"],
                                             fixture["away_name"])
        if not linedelta:
            type_text  = type_text_pattern.format(NotificationType.FIXTURE.value)
            delta_text = ''
        else:
            type_text  = type_text_pattern.format(linedelta.line_type.value)
            delta_text = '[{0}] moved FROM *{1}* TO *{2}*. Diff is - *{3}*'.\
                         format(linedelta.line, linedelta.prev_price,
                                linedelta.new_price, linedelta.delta)

        return " ".join([type_text, fixture_text, delta_text])
