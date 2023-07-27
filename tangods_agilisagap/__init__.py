from .AgilisAGAP import AgilisAGAP


def main():
    import sys
    import tango.server

    args = ["AgilisAGAP"] + sys.argv[1:]
    tango.server.run((AgilisAGAP,), args=args)
