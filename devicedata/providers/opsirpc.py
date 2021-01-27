import logging
import requests
import getpass
import base64
import os.path

# ignore warnings about missing ssl cert field subjectAltName (you may remove this and ln 102)
from requests.packages.urllib3.exceptions import SubjectAltNameWarning

opsicon_logger = logging.getLogger(__name__)


class OpsiError(Exception):

    def __init__(self, expression, opsierrorclass, message):
        """

        :param expression: the RPC Call
        :param opsierrorclass: the Error class
        :param message: the Error message
        """
        self.expression = expression
        self.opsierrorclass = opsierrorclass
        self.message = message


class OpsiConnection:

    def __init__(self, url, username=None, password=None, certfile=None, legal_methods_path=None):
        # 0 is not a valid id
        """

        :param url: Opsiserver URL
        :param authfile: base64 encoded UTF-8 String containing username password
        :param auth: username password as tuple
        :param certfile: Opsiserver SSL Certificate
        :param legal_methods_path: Textfile containing one method name per line
        """
        self.id = 0
        self.server = url
        self.certfile = certfile
        self.legal_methods = None
        auth = (username, password)
        # create session
        self.session = self.__get_session(auth)

        if legal_methods_path:
            opsicon_logger.debug("Get Methods from File...")
            if os.path.isfile(legal_methods_path):
                with open(legal_methods_path, 'r') as f:
                    self.legal_methods = f.read().splitlines()
            else:
                raise FileNotFoundError(legal_methods_path)
        else:
            # getPossibleMethods_listOfHashes lacks the modern _getObjects methods!
            opsicon_logger.debug("Get Methods from Server...")
            self.id += 1
            rjson = self.__rpc_request(self.session,
                                          {"method": "getPossibleMethods_listOfHashes",
                                           "params": [],
                                           "id": self.id})
            if rjson:
                self.legal_methods = []
            for method in rjson:
                self.legal_methods.append(method['name'])
            opsicon_logger.debug("Got Methods.")

    def raw_request(self, payload):
        """

        :param payload: json string to send to the server
        """
        self.__rpc_request(self.session, payload)

    def __getattr__(self, name):
        if name in self.legal_methods:
            def _rpc_call(*args, **kwargs):
                self.id += 1
                payload = {"method": name,
                           "params": [list(args)[1:], kwargs] if len(kwargs) > 0 else list(args)[1:],
                           "id": self.id}
                opsicon_logger.debug("Interpreting as rpc call: \n%s}" % payload)
                return self.__rpc_request(self.session, payload)

            return lambda *args, **kwargs: _rpc_call(self, *args, **kwargs)
        else:
            raise AttributeError

    def __get_session(self, auth):
        session = requests.Session()
        # avoid proxy issues
        session.trust_env = False
        # ignore warnings about missing ssl cert field subjectAltName
        requests.packages.urllib3.disable_warnings(SubjectAltNameWarning)
        # supply cert file
        if self.certfile:
            session.verify = self.certfile
        session.auth = auth
        opsicon_logger.debug("Created new session: %s}" % session)
        return session

    def __rpc_request(self, session, payload):
        try:
            r = session.post(self.server + '/rpc', json=payload, verify=False)
            r.raise_for_status()
        except requests.exceptions.Timeout as e:
            raise e
        except requests.exceptions.RequestException as e:
            raise e
        if r.json()["error"]:
            raise OpsiError(payload, r.json()['error']['class'], r.json()['error']['message'])
        return r.json()['result']
