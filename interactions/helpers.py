from enum import Enum
from django.db.models import Q


class ChoiceEnum(Enum):
    @classmethod
    def choices(cls):
        return [(c.name, c.value) for c in cls]


def make_words_fields_query_expr(words, fields, mode):
    assert mode in {'all', 'any'}
    q = None
    for w in words:
        w_q = None
        for f in fields:
            wf_q = Q(**{f + '__icontains': w})
            w_q = (w_q | wf_q) if w_q else wf_q
        if mode == 'all':
            q = (q & w_q) if q else w_q
        else:
            q = (q | w_q) if q else w_q
    return q
