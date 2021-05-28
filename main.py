from datetime import date
import logging

from utils.overridesHandler import getOverrides
import utils.configHandler as cfg

today = date.today()
dayDate = today.strftime("%d-%m-%Y")
_ov = getOverrides()

if _ov is not None and "DEBUG" in _ov:
    logging.basicConfig(format="%(levelname)s: %(module)s:  %(message)s", filename=f"templater-{dayDate}.log", level=logging.DEBUG)
else:
     logging.basicConfig(format="%(levelname)s: %(module)s:  %(message)s", filename=f"templater-{dayDate}.log", level=logging.INFO)   

def main():
    logging.debug('Entering main()')
    cfg.get_config()
    logging.debug('Exiting main()')


if __name__ == '__main__':
    main()
    