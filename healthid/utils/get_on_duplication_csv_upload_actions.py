import ast


def get_on_duplication_csv_upload_actions(on_duplication):
    try:
        on_duplication = ast.literal_eval(on_duplication)
        for key in on_duplication:
            value = on_duplication[key]
            del on_duplication[key]
            on_duplication[key.lower()] = value
    except Exception:
        on_duplication = on_duplication if type(on_duplication) is dict else {}
    return on_duplication
