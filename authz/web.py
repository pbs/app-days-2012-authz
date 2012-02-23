# -*- coding: utf-8 -*-
"""
    authz.web
    ~~~~~~~~~~~~~~

    Define Flask application endpoints

    :copyright: (c) 2012 by Ion Scerbatiuc
    :license: BSD
"""
import os.path

from flask import send_from_directory

from authz import application
app = application.create()


@app.route('/favicon.ico')
def favicon():
    """Server the favicon from the static folder."""
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon')


def runserver():
    """Run the Flask app with the internal server."""
    app.run(host='0.0.0.0', debug=True)


if __name__ == '__main__':
    runserver()
