import pandas as pd
from app import app
from flask import jsonify

# import dbconnection
from DatabaseConnection import *

def getStatementIdsForMerchantStatementFileCreation():
    try:
        query = ''' SELECT MS.STATEMENTID,MS.MID,MS.STATEMENTSTARTDATE,MS.STATEMENTENDDATE,MS.COMMISIONS,MS.FEES,MS.PAYMENT, MS.TOTALTXNAMOUNT,MS.BILLINGCYCLEID,MS.STATUS,MS.STARTEODID,MS.ENDEODID,MS.ACCOUNTNO,MS.STATEMENTGENERATEDSTATUS, ML.DESCRIPTION,ML.ADDRESS1,ML.ADDRESS2,ML.ADDRESS3,MS.TXNCOUNT FROM MERCHANTSTATEMENT MS INNER JOIN MERCHANTLOCATION ML ON MS.MID = ML.MERCHANTID WHERE MS.STATEMENTGENERATEDSTATUS = :status  '''

        df = pd.read_sql(query, con=conEngine(), params={"status": 0})

        return df

    except Exception as err:
        app.logger.error('Error in Merchant Statement controller {}'.format(str(err)))



def getDataFromStatementID(statementid, merchantid):
    global df2, df
    try:
        mainQuery = """SELECT MS.STATEMENTID,MS.MID,MS.STATEMENTSTARTDATE,MS.STATEMENTENDDATE,MS.COMMISIONS,MS.FEES,MS.PAYMENT, 
                 MS.TOTALTXNAMOUNT,MS.BILLINGCYCLEID,MS.STATUS,MS.STARTEODID,MS.ENDEODID,MS.ACCOUNTNO,MS.STATEMENTGENERATEDSTATUS, 
                 ML.DESCRIPTION,ML.ADDRESS1,ML.ADDRESS2,ML.ADDRESS3,MS.TXNCOUNT 
                 FROM MERCHANTSTATEMENT MS INNER JOIN MERCHANTLOCATION ML ON MS.MID = ML.MERCHANTID WHERE MS.STATEMENTGENERATEDSTATUS = 0 and MS.STATEMENTID= :statementid """

        df = pd.read_sql(mainQuery, con=conEngine(), params={"statementid": statementid})

        mid = df["mid"].values[0]
        starteod = df["starteodid"].values[0]
        endeod = df["endeodid"].values[0]

        query = '''SELECT EMC.MID,
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
  ((
  CASE
    WHEN EMC.CRDR = 'CR'
    THEN (0 - EMC.TRANSACTIONAMOUNT)
    ELSE EMC.TRANSACTIONAMOUNT
  END) - (
  CASE
    WHEN EMC.CRDR = 'CR'
    THEN (0 - EMC.MERCHANTCOMMSSION)
    ELSE EMC.MERCHANTCOMMSSION
  END)) AS GROSSAMOUNT,
  AA.TOTALGROSSAMOUNT
FROM EODMERCHANTCOMMISSION EMC
INNER JOIN EODMERCHANTTRANSACTION EMT
ON EMC.TRANSACTIONID = EMT.TRANSACTIONID
INNER JOIN
  (SELECT NVL(EMC.CARDASSOCIATION, 'QR') AS CARDASSOCIATION,
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
  WHERE 1=1
  AND EMC.MID = :mid
  AND EMC.STATUS          = 'EDON'
  AND EMC.ADJUSTMENTFLAG <> 2
  AND EMC.EODID > :starteod
  AND EMC.EODID <= :endeod
  GROUP BY EMC.CARDASSOCIATION
  ) AA
ON NVL(EMC.CARDASSOCIATION, 'QR') = AA.CARDASSOCIATION
INNER JOIN CURRENCY C
ON EMC.CURRENCYTYPE = C.CURRENCYNUMCODE
LEFT JOIN CARDASSOCIATION CA 
ON EMC.CARDASSOCIATION = CA.CODE
WHERE 1             =1
AND EMC.MID = :mid
AND EMC.STATUS          = 'EDON'
AND EMC.ADJUSTMENTFLAG <> 2
AND EMC.EODID > :starteod
AND EMC.EODID <= :endeod
ORDER BY EMC.CARDASSOCIATION,
  EMC.TRANSACTIONDATE'''
        df2 = pd.read_sql(query, con=conEngine(),
                          params={"mid": str(mid), "starteod": str(starteod),
                                  "endeod": str(endeod)})

    except Exception as err:
        print('Error ', err)

    return df, df2


def getDataToSubReportTWo(merchantid, statementStartDate, StatementEndDate):
    global df3
    try:
        query = '''SELECT F.DESCRIPTION,
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
AND EMF.MERCHANTID = :mid
AND TRUNC(EMF.EFFECTDATE) > TO_DATE(:statementstartdate ,'YYYY-MM-DD')
AND TRUNC(EMF.EFFECTDATE) <= TO_DATE(:statementenddate ,'YYYY-MM-DD')
AND EMF.STATUS = 'EDON'
ORDER BY EMF.EODID ASC'''
        df3 = pd.read_sql(query, con=conEngine(),
                          params={"mid": merchantid, "statementstartdate": str(statementStartDate)[:10],
                                  "statementenddate": str(StatementEndDate)[:10]})

    except Exception as err:
        app.logger.error('Error in get data from sub report one {}'.format(str(err)))
    return df3


def getSubReport1(merchantid):
    global df4
    try:
        query = """SELECT CASE WHEN ADJUSTMENTTYPE IN (4) AND CRDR = 'CR' THEN 'DR' WHEN ADJUSTMENTTYPE IN (4) AND CRDR = 'DR' THEN 'CR' ELSE CRDR END AS CRDR, ADJUSTMENTTYPE, AMOUNT, ADJUSTDATE, REMARKS FROM ACQADJUSTMENT WHERE 1=1 and MERCHANTID = :merchantid AND EODSTATUS  = 'EDON' AND ADJUSTMENTTYPE IN (1,2,4) ORDER BY ADJUSTDATE """
        df4 = pd.read_sql(query, con=conEngine(), params={"merchantid": merchantid})

    except Exception as err:
        app.logger.error('Error in conroller {}'.format(str(err)))
    return df4


def UpdateMerchantStatementStatus(statementid):

    global status
    status = 1

    try:
        con = conn()
        cursor = con.cursor()

        sql = ''' UPDATE MERCHANTSTATEMENT SET STATEMENTGENERATEDSTATUS = :status WHERE STATEMENTID = :statementid '''

        values = (status, statementid)

        cursor.execute(sql, values)

        con.commit()
        cursor.close()
        con.close()

    except Exception as err:
        app.logger.error('Error In Update Merchant Statement Status '.format(str(err)))
