#!/usr/bin/env python3

class Provider:

    @staticmethod
    def get_name(self):
        assert False

    @staticmethod
    def get_description(self):
        assert False
    
    @staticmethod
    def get_homepage(self):
        assert False

    def __init__(self, cfg):
        assert False

    def switch_server(self):
        assert False

    def get_server(self):
        """Returns (server-name,channel,parameters)
           channel can be:
              "pptp":
                 parameters: (common-options,username,password)
              "pptp-on-demand":
                 parameters: (common-options,username,password)
        """
        assert False