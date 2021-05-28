from datetime import date
import logging

from utils.overridesHandler import getOverrides
from utils.requestHandler import makeRequest
import utils.configHandler as cfg
from objects.requestObj import Request as ReqObj

today = date.today()
dayDate = today.strftime("%d-%m-%Y")
_ov = getOverrides()

if _ov is not None and "DEBUG" in _ov:
    logging.basicConfig(format="%(levelname)s: %(module)s:  %(message)s", filename=f"templater-{dayDate}.log", level=logging.DEBUG)
else:
     logging.basicConfig(format="%(levelname)s: %(module)s:  %(message)s", filename=f"templater-{dayDate}.log", level=logging.INFO)   

def main():
    logging.debug('Entering main()')
    config = cfg.get_config()
    profiles = cfg.get_profiles(config)
    
    logging.debug('Exiting main()')


if __name__ == '__main__':
    main()
    