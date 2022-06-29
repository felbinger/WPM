from pexpect import pxssh
from vymgmt import Router as VRouter


class Router(VRouter):
    def __init__(self, address, user, password='', port=22):
        super().__init__(address, user, password, port)
        self.__conn = None

    def login(self):
        """ Logins to the router

        """

        # XXX: after logout, old pxssh instance stops working,
        # so we create a new one for each login
        # There may or may not be a better way to handle it
        self.__conn = pxssh.pxssh(options=dict(StrictHostKeyChecking="no", UserKnownHostsFile="/dev/null"))

        self.__conn.login(self.__address, self.__user, password=self.__password, port=self.__port)
        self.__logged_in = True
