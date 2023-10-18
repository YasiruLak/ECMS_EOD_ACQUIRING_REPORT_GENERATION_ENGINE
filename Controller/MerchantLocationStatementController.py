from flask import send_file, request
from View.PDF import *
from app import app
from flask import jsonify


@app.route('/eod-engine/merchantLocation', methods=['POST'])
def generateMerchantLocationController():

    # get statementid, type, eodDate from springboot
    global successno, errorno
    eodDate = request.args.get("eodDate")

    try:
        successno, errorno = getToBeGenerateLocationFile(eodDate)
    except Exception as err:
        app.logger.error('Error in Merchant Location Statement controller {}'.format(str(err)))

    data = {'successno': successno, 'errorno': errorno}

    print(successno, errorno)
    return jsonify(data)

