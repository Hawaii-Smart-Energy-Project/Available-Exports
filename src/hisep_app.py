# -*- coding: utf-8 -*-

__author__ = 'Daniel Zhang (張道博)'
__copyright__ = 'Copyright (c) 2014, Daniel Zhang (張道博)'


import sys
import ConfigParser
from authomatic import Authomatic
from authomatic.adapters import WerkzeugAdapter
from authomatic.providers import oauth2
from flask import Flask, request, make_response
from flask.ext.sqlalchemy import SQLAlchemy
import logging
import markdown2
import os


class Configer(object):
    def __init__(self):
        self._config = ConfigParser.ConfigParser()
        configFilePath = '.available-exports-app.cfg'

        try:
            self._config.read(['site.cfg', configFilePath])
        except:
            logging.error("Critical error: The data in {} cannot be "
                          "accessed successfully.".format(configFilePath))
            sys.exit(-1)


    def configOptionValue(self, section, option):
        """
        Get a configuration value from the local configuration file.
        :param section: String of section in config file.
        :param option: String of option in config file.
        :returns: The value contained in the configuration file.
        """
        try:
            configValue = self._config.get(section, option)
            if configValue == "True":
                return True
            elif configValue == "False":
                return False
            else:
                return configValue
        except:
            logging.error(
                "Failed when getting configuration option {} in section {"
                "}.".format(option, section))
            sys.exit(-1)


configer = Configer()
SECURITY = 'Security'

logging.basicConfig(filename = 'app.log', level = logging.INFO)
logging.info('name: %s' % __name__)
app = Flask(__name__)

app.config['SECRET_KEY'] = configer.configOptionValue(SECURITY, 'app_secret')
basedir = os.path.abspath(os.path.dirname(__file__))
dbName = 'db.sqlite'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, dbName)
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,
                                                                    dbName)
app.config['SECURITY_PASSWORD_HASH'] = 'pbkdf2_sha512'
app.config['SECURITY_PASSWORD_SALT'] = configer.configOptionValue(SECURITY,
                                                                  'app_salt')
app.config['SECURITY_POST_LOGIN'] = '/profile'

# Extensions.
db = SQLAlchemy(app)

CONFIG = {'google': {'class_': oauth2.Google,
                     'consumer_key': configer.configOptionValue(SECURITY,
                                                                'google_consumer_key'),
                     'consumer_secret': configer.configOptionValue(SECURITY,
                                                                   'google_consumer_secret'),
                     'scope': oauth2.Google.user_info_scope + [
                         'https://www.googleapis.com/auth/userinfo.profile'], }, }

authomatic = Authomatic(CONFIG, configer.configOptionValue(SECURITY,
                                                           'authomatic_secret'))


def validUser(email):
    global configer
    try:
        validUsers = eval(configer.configOptionValue(SECURITY, 'valid_users'))
        logging.info('validUsers {}'.format(validUsers))
        if email in validUsers:
            return True
        return False
    except Exception as detail:
        logging.error('Exception: {}'.format(detail))


@app.route('/submit-data', methods = ['POST'])
def handle_data():
    """
    Send data to the server to be saved and displayed.
    """

    logging.info('posting data')
    fp = open('export-files.txt', 'wb')
    fp.write(tableCSS())
    fp.write(markdown2.markdown(exportRecoveryInstructions(),
                                extras = ["wiki-tables"]))
    fp.write(markdown2.markdown(request.data, extras = ["wiki-tables"]))
    fp.write('\n</body>\n')
    fp.write('</html>\n')
    fp.close()
    logging.info('data=%s' % request.data)
    return request.data


def view_function(result):
    return "view_function: %s" % result


# @IMPORTANT
@app.route('/export/files', methods = ['GET', 'POST'])
def list_exports():
    """
    List the available HISEP exports.
    """

    os.environ['SCRIPT_NAME'] = ''

    result = None
    logging.info('Listing exports')
    response = make_response(
        '<html><head><meta name = "robots" content = '
        '"noindex"></head><body>Not available. If you have a valid account '
        'please try again using <a href="http://ikiapps'
        '.com/hisep/export/files">http://ikiapps'
        '.com/hisep/export/files</a>.</body></html>')
    result = authomatic.login(WerkzeugAdapter(request, response), 'google')
    authenticated = False
    validEmail = False

    if result:
        if result.user:
            logging.info('Got result.user, email: %s', result.user.email)
            result.user.update()

            if result.user.credentials:
                logging.info(
                    'Got result.user.credentials, email: %s' % result.user
                    .email)
                if validUser(result.user.email):
                    authenticated = True
                validEmail = True

    if authenticated:
        logging.info('Requesting export files.')

        fp = open('export-files.txt', 'rb')
        data = fp.read()
        fp.close()

        return data

    else:
        logging.info('Not authenticated.')

    if validEmail:
        response = make_response('Access denied for %s.' % result.user.email)
        return response

    # @CRITICAL: This is necessary for Google authentication to work.
    logging.info('-> Returning response: %s' % response)

    return response


def exportRecoveryInstructions():
    """
    Add recovery instructions.
    """
    fp = open('recovery-instructions.md', 'rb')
    data = fp.read()
    fp.close()
    return data


def tableCSS():
    """
    Add CSS and HTML content.
    """
    fp = open('export-page.css', 'rb')
    data = fp.read()
    fp.close()
    return data


