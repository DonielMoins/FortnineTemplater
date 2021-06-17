from datetime import date
from gui.GUI import GUIProc
import logging

from utils.settings import getOverrides
from utils.requests import makeRequest, ReqObj


today = date.today()
dayDate = today.strftime("%d-%m-%Y")
_ov = getOverrides()
threads = {}

if _ov is not None and "DEBUG" in _ov:
    logging.basicConfig(format="%(levelname)s: %(module)s:  %(message)s", filename=f"templater-{dayDate}.log", level=logging.DEBUG)
else:
    logging.basicConfig(format="%(levelname)s: %(module)s:  %(message)s", filename=f"templater-{dayDate}.log", level=logging.INFO)   

def main():
    logging.debug('Entering main()')
    # config = cfg.get_config()
    # profiles = cfg.get_profiles(config)
    GUIProc.start()
    threads["GUI"] = GUIProc
    while(threads):
        if not threads["GUI"].is_alive():
            for name, thread in threads.items():
                if name != "GUI":
                    thread.join()
            break
    logging.debug('Exiting main()')
    
            

if __name__ == '__main__':
    main()
    