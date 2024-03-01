#!/usr/bin/env python

import os
import json


import pytolino
import xdg_base_dirs


def get_calibre_db():
    """search in home calibre db
    :returns: path to calibre db

    """
    calibre_config_fn = 'global.py.json'
    calibre_folder = 'calibre'
    db_fn = 'metadata.db'
    library_config_key = 'library_path'
    folder = os.path.join(xdg_base_dirs.xdg_config_home(), calibre_folder)
    calibre_config_path = os.path.join(folder, calibre_config_fn)
    with open(calibre_config_path) as myfile:
        config = json.load(myfile)
    db_folder = config[library_config_key]
    db_path = os.path.join(db_folder, db_fn)
    if os.path.exists(db_path):
        return db_path
    else:
        return None


def run():
    """ function to be executed as entry point to upload the data

    """
    print('a script to upload the calibre library')
    print('script not yet ready...')


if __name__ == '__main__':
    path = get_calibre_db()
    print(path)
