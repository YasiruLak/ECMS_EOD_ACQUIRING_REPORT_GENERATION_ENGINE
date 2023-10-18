from flask import send_file, request
from View.PDF import *
from app import app
from flask import jsonify


@app.route('/eod-engine/merchantCustomer', methods=['POST'])
def generateMerchantCustomerController():

    # get eodDate from springboot
    global successno, errorno
    eodDate = request.args.get("eodDate")
    EODDATE = eodDate

    try:
        successno, errorno = getToBeGenerateCustomerFile(eodDate)
    except Exception as err:
        app.logger.error('Error in Merchant Customer Statement controller {}'.format(str(err)))

    data = {'successno': successno, 'errorno': errorno}

    return jsonify(data)
