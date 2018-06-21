import pprint
import json


pp = pprint.PrettyPrinter(indent=2).pprint


def print_json(label, data):
    print("\n=== {}:".format(label),
          json.dumps(data, indent=2),
          "\n=== /{}\n".format(label))


def get_item(target_list, field, value):
    r = [it for it in target_list if it[field] == value]
    assert len(r) == 1
    return r[0]
