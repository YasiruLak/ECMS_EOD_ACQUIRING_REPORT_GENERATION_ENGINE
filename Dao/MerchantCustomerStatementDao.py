import pandas as pd
from app import app

# import dbconnection
from DatabaseConnection import *

def getStatementIdsForMerchantCustomerStatementFileCreation():
    try:
        query = '''SELECT MCS.STATEMENTID, MCS.MERCHANTCUSNO, MCS.STATEMENTSTARTDATE, MCS.STATEMENTENDDATE, MCS.COMMISIONS, MCS.FEES, MCS.PAYMENT, MCS.TOTALTXNAMOUNT, MCS.BILLINGCYCLEID, MCS.STATUS, MCS.STARTEODID, MCS.ENDEODID, MCS.ACCOUNTNO, MCS.STATEMENTGENERATEDSTATUS, MC.MERCHANTNAME, MC.ADDRESS1, MC.ADDRESS2, MC.ADDRESS3 FROM MERCHANTCUSTOMERSTATEMENT MCS INNER JOIN MERCHANTCUSTOMER MC ON MCS.MERCHANTCUSNO = MC.MERCHANTCUSTOMERNO WHERE MCS.STATEMENTGENERATEDSTATUS = :status '''

        df = pd.read_sql(query, con=conEngine(), params={"status": 0})

        return df

    except Exception as err:
        app.logger.error('Error in Merchant Statement controller {}'.format(str(err)))

def getDataFromMainQuery(statementid):
    try:
        query = """ SELECT MCS.STATEMENTID,
                  MCS.MERCHANTCUSNO,
                  MCS.STATEMENTSTARTDATE,
                  MCS.STATEMENTENDDATE,
                  MCS.COMMISIONS,
                  MCS.FEES,
                  MCS.PAYMENT,
                  MCS.TOTALTXNAMOUNT,
                  MCS.BILLINGCYCLEID,
                  MCS.STATUS,
                  MCS.STARTEODID,
                  MCS.ENDEODID,
                  MCS.ACCOUNTNO,
                  MCS.STATEMENTGENERATEDSTATUS,
                  MC.MERCHANTNAME,
                  MC.ADDRESS1,
                  MC.ADDRESS2,
                  MC.ADDRESS3 
                FROM MERCHANTCUSTOMERSTATEMENT MCS 
                INNER JOIN MERCHANTCUSTOMER MC 
                ON MCS.MERCHANTCUSNO = MC.MERCHANTCUSTOMERNO 
                WHERE MCS.STATEMENTGENERATEDSTATUS = 0
                AND MCS.STATEMENTID=:statementid """

        df = pd.read_sql(query, con=conEngine(), params={"statementid": statementid})


    except Exception as err:
        app.logger.error('Error while getting data {}'.format(str(err)))

    return df


def getDataToCustomerStatement(merchantCusNo, startEodID, endeodid):
    global df
    try:
        query = """SELECT EMC.MID,
                  ML.DESCRIPTION AS MERCHANTNAME,
                  NVL(CA.DESCRIPTION,'QR') AS CARDASSOCIATION,
                  EMC.PRODUCTID,
                  EMC.TID,
                  EMC.CRDR,
                  EMC.TRANSACTIONDATE,
                  EMT.SETTLEMENTDATE,
                  EMC.TRANSACTIONID,
                  EMT.CARDNUMBER,
                  C.CURRENCYALPHACODE AS CURRENCYTYPE,
                  CASE
                    WHEN EMC.CRDR = 'CR'
                    THEN (0 - EMC.TRANSACTIONAMOUNT)
                    ELSE EMC.TRANSACTIONAMOUNT
                  END AS TRANSACTIONAMOUNT,
                  CASE
                    WHEN EMC.CRDR = 'CR'
                    THEN (0 - EMC.MERCHANTCOMMSSION)
                    ELSE EMC.MERCHANTCOMMSSION
                  END AS MERCHANTCOMMSSION,
                  EMT.AUTHCODE,
                  AA.TOTALTXNAMOUNT,
                  AA.TOTALTXNCOUNT,
                  AA.TOTALMERCHANTCOMISSION,
                  ( (CASE
                    WHEN EMC.CRDR = 'CR'
                    THEN (0 - EMC.TRANSACTIONAMOUNT)
                    ELSE EMC.TRANSACTIONAMOUNT
                  END) - (CASE
                    WHEN EMC.CRDR = 'CR'
                    THEN (0 - EMC.MERCHANTCOMMSSION)
                    ELSE EMC.MERCHANTCOMMSSION
                  END)) AS GROSSAMOUNT,
                  AA.TOTALGROSSAMOUNT
                FROM EODMERCHANTCOMMISSION EMC
                INNER JOIN EODMERCHANTTRANSACTION EMT
                ON EMC.TRANSACTIONID = EMT.TRANSACTIONID
                INNER JOIN
                  (SELECT EMC.MID,
                    NVL(EMC.CARDASSOCIATION, 'QR') AS CARDASSOCIATION,
                    SUM(
                    CASE
                      WHEN EMC.CRDR = 'CR'
                      THEN (0 - EMC.TRANSACTIONAMOUNT)
                      ELSE EMC.TRANSACTIONAMOUNT
                    END)                     AS TOTALTXNAMOUNT,
                    COUNT(EMC.TRANSACTIONID) AS TOTALTXNCOUNT,
                    SUM(
                    CASE
                      WHEN EMC.CRDR = 'CR'
                      THEN (0 - EMC.MERCHANTCOMMSSION)
                      ELSE EMC.MERCHANTCOMMSSION
                    END) AS TOTALMERCHANTCOMISSION,
                    ( SUM(
                    CASE
                      WHEN EMC.CRDR = 'CR'
                      THEN (0 - EMC.TRANSACTIONAMOUNT)
                      ELSE EMC.TRANSACTIONAMOUNT
                    END) - SUM(
                    CASE
                      WHEN EMC.CRDR = 'CR'
                      THEN (0 - EMC.MERCHANTCOMMSSION)
                      ELSE EMC.MERCHANTCOMMSSION
                    END) ) AS TOTALGROSSAMOUNT
                  FROM EODMERCHANTCOMMISSION EMC
                  WHERE 1                 =1
                  AND EMC.MERCHANTCUSTID  = :merchantCusNo
                  AND EMC.STATUS          = 'EDON'
                  AND EMC.ADJUSTMENTFLAG <> 2
                  AND EMC.EODID > :startEodID
                  AND EMC.EODID <= :endeodid
                  GROUP BY EMC.MID,
                    EMC.CARDASSOCIATION
                  ) AA
                ON EMC.MID              = AA.MID
                AND NVL(EMC.CARDASSOCIATION, 'QR') = AA.CARDASSOCIATION
                INNER JOIN CURRENCY C
                ON EMC.CURRENCYTYPE = C.CURRENCYNUMCODE
                LEFT JOIN CARDASSOCIATION CA 
                ON EMC.CARDASSOCIATION = CA.CODE
                INNER JOIN MERCHANTLOCATION ML
                ON EMC.MID              = ML.MERCHANTID
                WHERE 1                 =1
                AND EMC.MERCHANTCUSTID  = :merchantCusNo
                AND EMC.STATUS          = 'EDON'
                AND EMC.ADJUSTMENTFLAG  <> 2
                AND EMC.EODID > :startEodID
                AND EMC.EODID <= :endeodid
                ORDER BY EMC.MID,
                  EMC.CARDASSOCIATION,
                  EMC.TRANSACTIONDATE"""

        df = pd.read_sql(query, con=conEngine(), params={"merchantCusNo": merchantCusNo,
                                                         "startEodID": str(startEodID),
                                                         "endeodid": str(endeodid)})

    except Exception as err:
        app.logger.error('Error while getting data {}'.format(str(err)))

    return df


def getDataforAdjusmentReport(mid, statementStartDate, statementEndDate):
    # query = """SELECT CASE
    # WHEN ADJUSTMENTTYPE IN (4) AND CRDR = 'CR'
    # THEN 'DR'
    # WHEN ADJUSTMENTTYPE IN (4) AND CRDR = 'DR'
    # THEN 'CR'
    # ELSE CRDR
    # END AS CRDR,
    # ADJUSTMENTTYPE,
    #   AMOUNT,
    #   ADJUSTDATE,
    #   REMARKS
    # FROM ACQADJUSTMENT
    # WHERE 1=1
    # AND MERCHANTID = :mid
    # --$P!{mId_sql}
    # --AND $P!{StatementStartDate_sql}
    # and TRUNC(ADJUSTDATE) > TO_DATE(:statementStartDate,'DD-MM-YY')
    # --AND $P!{StatementEndDate_sql}
    # and TRUNC(ADJUSTDATE) <= TO_DATE(:statementEndDate ,'DD-MM-YY')
    # AND EODSTATUS  = 'EDON'
    # AND ADJUSTMENTTYPE IN (1,2,4)
    # ORDER BY ADJUSTDATE"""
    global adjusmentDs
    query = """SELECT CASE
    WHEN ADJUSTMENTTYPE IN (4) AND CRDR = 'CR'
    THEN 'DR'
    WHEN ADJUSTMENTTYPE IN (4) AND CRDR = 'DR'
    THEN 'CR'
    ELSE CRDR
    END AS CRDR,
    ADJUSTMENTTYPE,
      AMOUNT,
      ADJUSTDATE,
      REMARKS
    FROM ACQADJUSTMENT
    WHERE 1=1
    AND MERCHANTID = :mid
    --$P!{mId_sql}
    --AND $P!{StatementStartDate_sql}
    --and TRUNC(ADJUSTDATE) > TO_DATE(:statementStartDate,'DD-MM-YY')
    --AND $P!{StatementEndDate_sql}
    --and TRUNC(ADJUSTDATE) <= TO_DATE(:statementEndDate ,'DD-MM-YY')
    AND EODSTATUS  = 'EDON'
    --AND ADJUSTMENTTYPE IN (1,2,4)
    ORDER BY ADJUSTDATE"""

    try:
        # adjusmentDs = pd.read_sql(query, con=conEngine(), params={"mid": mid,
        #                                                           "statementStartDate": str(statementStartDate),
        #                                                           "statementEndDate": str(statementEndDate)})
        adjusmentDs = pd.read_sql(query, con=conEngine(), params={"mid": mid})

    except Exception as err:
        app.logger.error('Error while getting data for adjustment report '.format(str(err)))

    return adjusmentDs


def getDataforFees(merchantid,statementStartDate, statementEndDate):
    query = """SELECT F.DESCRIPTION,
          EMF.EFFECTDATE,
          EMF.CRDR,
          CASE
            WHEN EMF.CRDR = 'DR'
            THEN (-EMF.FEEAMOUNT)
            ELSE EMF.FEEAMOUNT
          END AS FEEAMOUNT
        FROM EODMERCHANTFEE EMF
        INNER JOIN FEE F
        ON EMF.FEETYPE = F.FEECODE
        WHERE 1        =1
        AND EMF.MERCHANTID = :merchantid
        --AND TRUNC(EMF.EFFECTDATE) > TO_DATE(:statementStartDate,'DD-MM-YY')
        --AND TRUNC(EMF.EFFECTDATE) <= TO_DATE(:statementEndDate,'DD-MM-YY')
        AND EMF.STATUS = 'EDON'
        ORDER BY EMF.EODID ASC"""
    try:
        # df3 = pd.read_sql(query, con=conEngine(), params={"merchantid": merchantid,
        #                                                   "statementStartDate": str(statementStartDate),
        #                                                   "statementEndDate": str(statementEndDate)})
        df3 = pd.read_sql(query, con=conEngine(), params={"merchantid": merchantid})

    except Exception as err:
        app.logger.error('Error while getting data for fees sub report '.format(str(err)))
    return df3

def UpdateMerchantCustomerStatementStatus(statementid):

    global status
    status = 1

    try:
        con = conn()
        cursor = con.cursor()

        sql = ''' UPDATE MERCHANTCUSTOMERSTATEMENT SET STATEMENTGENERATEDSTATUS = :status WHERE STATEMENTID = :statementid '''

        values = (status, statementid)

        cursor.execute(sql, values)

        con.commit()
        cursor.close()
        con.close()

    except Exception as err:
        app.logger.error('Error In Update Merchant Customer Statement Status '.format(str(err)))


# def UpdateEodMerchantCustomerPaymentTableBillingDone(statementid):
#
#     try:
#         con = conn()
#         cursor = con.cursor()
#
#         sql = ''' UPDATE EODMERCHANTPAYMENT SET STATUS='MCBC' WHERE MERCHANTCUSTID = :statementid AND STATUS='EPEN'  '''
#
#         values = (statementid)
#
#         cursor.execute(sql, values)
#
#         con.commit()
#         cursor.close()
#         con.close()
#
#     except Exception as err:
#         app.logger.error('Error In Update Merchant Customer Statement Status '.format(str(err)))


        

