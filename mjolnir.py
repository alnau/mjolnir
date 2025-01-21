import utility
from app import App

import logging
import sys


utility.initializeWorkspace()
config = utility.readIni()

logging.basicConfig(
    filename=utility.resourcePath('tmp\mjolnir.log'),  
    level=logging.ERROR,        
    format='%(asctime)s - %(levelname)s - %(message)s'  
)

def log_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    print("Uncaught exception", exc_type, exc_value, exc_traceback)
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


def main():

    sys.excepthook = log_exception
    app = App(config)
    

        



if __name__ == "__main__":
    main()