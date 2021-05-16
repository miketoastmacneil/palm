


def symbol_from_filename(filename: str):
    """
    Assumes the filename to be <path>/<symbol>.csv or <path>/<symbol>.json
    """

    return filename.split('/')[-1].split('.')[-2]