import os
from Utils import *
from Utils.Configuration import PATTERN_CHAR, END_INDEX, START_INDEX
from app import app
import platform


def generateFilePath(statementid, type, eodDate, merchantid):
    os_name = platform.system()
    global filePathDate, filepath, filename, filepathtopan
    datetemp = str(eodDate)
    date = "20" + datetemp[0:2] + "-" + datetemp[2:4] + "-" + datetemp[4:6]

    try:
        if os_name.upper() == 'WINDOWS':

            if type == 'Location':
                filepath = MERCHANT_STATEMENT_PATH + '\\' + merchantid + '\\'
                filepathtopan = MERCHANT_STATEMENT_PATH + MERCHANT_STATEMENT_TOPAN_FILE_PATH + '\\'
            elif type == 'Customer':
                filepath = MERCHANT_CUSTOMER_STATEMENT_PATH + '\\' + merchantid + '\\'
                filepathtopan = MERCHANT_CUSTOMER_STATEMENT_PATH + MERCHANT_STATEMENT_TOPAN_FILE_PATH + "\\"

            filePathDate = filepathtopan + '\\' + date + '\\'

        else:
            if type == 'Location':
                filepath = MERCHANT_STATEMENT_PATH + '/' + merchantid + '/'
                filepathtopan = MERCHANT_STATEMENT_PATH + MERCHANT_STATEMENT_TOPAN_FILE_PATH + '/'
            elif type == 'Customer':
                filepath = MERCHANT_CUSTOMER_STATEMENT_PATH + '/' + merchantid + '/'
                filepathtopan = MERCHANT_CUSTOMER_STATEMENT_PATH + MERCHANT_STATEMENT_TOPAN_FILE_PATH + '/'

            filePathDate = filepathtopan + date + '/'

        # Create a new directory  in the 'C:\' directory
        path = os.path.join(filepath)
        if not os.path.exists(path):
            os.makedirs(path)
            app.logger.info('directory was created')
        else:
            app.logger.info('directory already exists.')

        filename = filepath + statementid + ".pdf"

    except Exception as err:
        app.errorhandler.logger.error('Error in Service {}'.format(str(err)))

    return filePathDate, filepath, filename


