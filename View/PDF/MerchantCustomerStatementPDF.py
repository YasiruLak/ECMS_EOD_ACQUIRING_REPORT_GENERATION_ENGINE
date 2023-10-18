import numpy as np
from reportlab.graphics import shapes
from reportlab.platypus import SimpleDocTemplate

import Dao.MerchantCustomerStatementDao
from Dao import *
from Dao import MerchantCustomerStatementDao
from app import app
from Service import *
from Utils import *
from reportlab.lib import colors


def getToBeGenerateCustomerFile(eodDate):
    global statementid, merchantid, type, successno, errorno

    try:
        df = Dao.getStatementIdsForMerchantCustomerStatementFileCreation()
        successno = 0
        errorno = 0
        for ind in df.index:
            errorcount = errorno
            successcount = successno
            statementid = df['statementid'][ind]
            merchantid = df['merchantcusno'][ind]
            type = 'Customer'
            successno, errorno = genarateMerchantCustomerStatement(statementid, type, eodDate, merchantid, errorcount,
                                                                   successcount)

    except Exception as err:
        app.logger.error('Error in Merchant Customer Statement controller {}'.format(str(err)))

    return successno, errorno


def genarateMerchantCustomerStatement(statementid, type, eodDate, merchantid, errorcount, successcount):
    totalAdjCommission = 0.00
    totalAdjGross = 0.00
    totalAdj = 0.00
    totalfee = 0.00

    try:
        # get data from db
        df1 = Dao.MerchantCustomerStatementDao.getDataFromMainQuery(statementid)
        df2 = MerchantCustomerStatementDao.getDataToCustomerStatement(df1["merchantcusno"].values[0],
                                                                      df1["starteodid"].values[0],
                                                                      df1["endeodid"].values[0])
        filePathDate, filepath, filename = generateFilePath(statementid, type, eodDate, merchantid)
        # define page size and create a SimpleDocTemplate object
        page_size = (595, 842)
        BottomMargin = 24
        TopMargin = 4
        LeftMargin = 4
        RightMargin = 4
        doc = SimpleDocTemplate(filename, pagesize=page_size, bottomMargin=BottomMargin, topMargin=TopMargin,
                                leftMargin=LeftMargin, rightMargin=RightMargin)

        # Create heading box drawing with rectangle
        heading_box_x = 0
        heading_box_y = 0
        heading_box_width = 580
        heading_box_height = 70

        heading_box = shapes.Drawing(heading_box_width, heading_box_height)

        HeadingBackground = shapes.Rect(heading_box_x, heading_box_y, heading_box_width, heading_box_height,
                                        fillColor=colors.white,
                                        strokeColor=colors.white)

        heading_box.add(HeadingBackground)
        df1['merchantname'] = np.where(df1['merchantname'].isna().any(), ' ', df1['merchantname'])
        df1['address1'] = np.where(df1['address1'].isna().any(), ' ', df1['address1'])
        df1['address2'] = np.where(df1['address2'].isna().any(), ' ', df1['address2'])
        df1['address3'] = np.where(df1['address3'].isna().any(), ' ', df1['address3'])
        # --------------------- add content-------------------------
        merchantName = shapes.String(10, 60, df1["merchantname"].values[0], fontName="Helvetica-Bold", fontSize=10,
                                     fillColor=colors.black)
        heading_box.add(merchantName)
        # report_name = shapes.String(30, 20, 'Card Number Generation Report', fontName="Helvetica-Bold", fontSize=12,
        #                             fillColor=colors.white)
        # heading_box.add(report_name)
        addr1 = shapes.String(10, 45, df1["address1"].values[0], fontName="Helvetica", fontSize=8,
                              fillColor=colors.black)
        heading_box.add(addr1)
        addr2 = shapes.String(10, 35, df1["address2"].values[0], fontName="Helvetica", fontSize=8,
                              fillColor=colors.black)
        heading_box.add(addr2)
        addr3 = shapes.String(10, 25, df1["address3"].values[0], fontName="Helvetica", fontSize=8,
                              fillColor=colors.black)
        heading_box.add(addr3)
        report_name = shapes.String(130, 10, 'Transaction Detail Report From : ', fontName="Helvetica", fontSize=8)
        heading_box.add(report_name)
        date_string = str(df1["statementstartdate"].values[0])
        from_date = shapes.String(250, 10, date_string[:10], fontName="Helvetica", fontSize=8)
        heading_box.add(from_date)
        string_to = shapes.String(320, 10, 'To', fontName="Helvetica", fontSize=8)
        heading_box.add(string_to)
        date_string2 = str(df1["statementenddate"].values[0])
        to_date = shapes.String(350, 10, date_string2[:10], fontName="Helvetica", fontSize=8)
        heading_box.add(to_date)

        # create the content for the template
        elements = []
        # add itemes
        elements.append(heading_box)

        # herozontal line
        column_header_x = 0
        column_header_y = 0

        herizontal_line = shapes.Drawing(580, 2)
        r1 = shapes.Rect(column_header_x, column_header_y, 580, 2,
                         fillColor=colors.black,
                         strokeColor=colors.black)
        herizontal_line.add(r1)
        elements.append(herizontal_line)

        # colunm headers
        column_header_x = 0
        column_header_y = 0
        column_header_width = 580
        column_header_height = 20

        column_header = shapes.Drawing(column_header_width, column_header_height)
        r1 = shapes.Rect(column_header_x, column_header_y, column_header_width, column_header_height,
                         fillColor=colors.white,
                         strokeColor=colors.white)
        column_header.add(r1)

        # --------------------- add content-------------------------
        string_cardnumber = shapes.String(10, 10, 'CARD NUMBER / ACCOUNT NO', fontName="Helvetica-Bold", fontSize=8)
        column_header.add(string_cardnumber)
        string_posid = shapes.String(140, 10, 'POS ID', fontName="Helvetica-Bold", fontSize=8)
        column_header.add(string_posid)
        string_auth = shapes.String(200, 10, 'AUTH', fontName="Helvetica-Bold", fontSize=8)
        column_header.add(string_auth)
        string_grossamt = shapes.String(260, 10, 'GROSS AMT', fontName="Helvetica-Bold", fontSize=8)
        column_header.add(string_grossamt)
        string_netamt = shapes.String(320, 10, 'NET AMT', fontName="Helvetica-Bold", fontSize=8)
        column_header.add(string_netamt)
        string_comission = shapes.String(380, 10, 'COMMISSION', fontName="Helvetica-Bold", fontSize=8)
        column_header.add(string_comission)
        string_trandate = shapes.String(440, 10, 'TRAN DATE', fontName="Helvetica-Bold", fontSize=8)
        column_header.add(string_trandate)
        string_postdate = shapes.String(500, 10, 'POST DATE', fontName="Helvetica-Bold", fontSize=8)
        column_header.add(string_postdate)

        elements.append(column_header)
        # add horizontal line
        elements.append(herizontal_line)

        # Create merchan grup header box drawing with rectangle
        date_box_x = 0
        date_box_y = 0
        date_box_width = 580
        date_box_height = 20

        # get data from query 2
        for ind in df2.index:

            # merchant group header
            merchant_group_header = shapes.Drawing(date_box_width, date_box_height)
            r1 = shapes.Rect(date_box_x, date_box_y, date_box_width, date_box_height, fillColor=colors.white,
                             strokeColor=colors.white)
            merchant_group_header.add(r1)
            merchant_group_string = df2['mid'][ind] + " - " + df2['merchantname'][ind]
            string_mid = shapes.String(10, 10, merchant_group_string, fontName="Helvetica", fontSize=8)
            merchant_group_header.add(string_mid)
            elements.append(merchant_group_header)

            # card type group header
            card_type_header = shapes.Drawing(date_box_width, date_box_height)
            r1 = shapes.Rect(date_box_x, date_box_y, date_box_width, date_box_height, fillColor=colors.white,
                             strokeColor=colors.white)
            card_type_header.add(r1)
            string_cardassociation = shapes.String(10, 10, df2['cardassociation'][ind], fontName="Helvetica",
                                                   fontSize=8)
            card_type_header.add(string_cardassociation)
            elements.append(card_type_header)

            # detail1
            detail1 = shapes.Drawing(date_box_width, date_box_height)
            r1 = shapes.Rect(date_box_x, date_box_y, date_box_width, date_box_height, fillColor=colors.white,
                             strokeColor=colors.white)
            detail1.add(r1)
            # --------------------- add content-------------------------
            card_number = df2['cardnumber'][ind]
            start_index = START_INDEX
            end_index = END_INDEX
            pattern = PATTERN_CHAR[0] * (END_INDEX - START_INDEX)
            content_cardnumber = shapes.String(10, 10, card_number[:start_index] + pattern + card_number[end_index:],
                                               fontName="Helvetica", fontSize=8)
            detail1.add(content_cardnumber)
            string_posid = shapes.String(140, 10, df2['tid'][ind], fontName="Helvetica", fontSize=8)
            detail1.add(string_posid)
            content_auth = shapes.String(200, 10, df2['authcode'][ind], fontName="Helvetica", fontSize=8)
            detail1.add(content_auth)
            content_grossamt = shapes.String(260, 10, str(float(df2['transactionamount'][ind])), fontName="Helvetica",
                                             fontSize=8)
            detail1.add(content_grossamt)
            content_netamt = shapes.String(320, 10, str(float(df2['grossamount'][ind])), fontName="Helvetica",
                                           fontSize=8)
            detail1.add(content_netamt)
            content_comission = shapes.String(380, 10, str(float(df2['merchantcommssion'][ind])), fontName="Helvetica",
                                              fontSize=8)
            detail1.add(content_comission)
            # date_string2 = str(StatementEndDate)
            # pdf.drawString(320, 135, date_string2[:10])
            content_trandate = shapes.String(440, 10, str(df2['transactiondate'][ind])[:10], fontName="Helvetica",
                                             fontSize=8)
            detail1.add(content_trandate)
            content_postdate = shapes.String(500, 10, str(df2['settlementdate'][ind])[:10], fontName="Helvetica",
                                             fontSize=8)
            detail1.add(content_postdate)
            elements.append(detail1)

            # card type group footer
            card_type_footer = shapes.Drawing(date_box_width, date_box_height)
            r1 = shapes.Rect(date_box_x, date_box_y, date_box_width, date_box_height, fillColor=colors.white,
                             strokeColor=colors.white)
            card_type_footer.add(r1)

            content_subtotal = shapes.String(10, 10, 'SUB TOTAL : ', fontName="Helvetica", fontSize=8)
            card_type_footer.add(content_subtotal)
            if df2['totaltxnamount'][ind] is None:
                txnamt = 0.00
            else:
                txnamt = float(df2['totaltxnamount'][ind])
            content_txn = shapes.String(260, 10, str(txnamt), fontName="Helvetica", fontSize=8)
            card_type_footer.add(content_txn)
            if df2['totalgrossamount'][ind] is None:
                ttlgrossamt = 0.00
            else:
                ttlgrossamt = float(df2['totalgrossamount'][ind])
            content_ttlgrossamount = shapes.String(320, 10, str(ttlgrossamt), fontName="Helvetica", fontSize=8)
            card_type_footer.add(content_ttlgrossamount)
            if df2['merchantcommssion'][ind] is None:
                commision = 0.00
            else:
                commision = float(df2['merchantcommssion'][ind])
            content_commision = shapes.String(380, 10, str(commision), fontName="Helvetica", fontSize=8)
            card_type_footer.add(content_commision)

            elements.append(card_type_footer)

        #########################################
        # sub report 1 (adjusment)
        adj = Dao.MerchantCustomerStatementDao.getDataforAdjusmentReport(df2["mid"].values[0],
                                                                         df1["starteodid"].values[0],
                                                                         df1["endeodid"].values[0])
        adjesment = shapes.Drawing(date_box_width, date_box_height)
        r1 = shapes.Rect(date_box_x, date_box_y, date_box_width, date_box_height, fillColor=colors.white,
                         strokeColor=colors.white)
        adjesment.add(r1)
        string_fees = shapes.String(10, 10, 'ADJUSTMENTS', fontName="Helvetica", fontSize=8)
        adjesment.add(string_fees)
        elements.append(adjesment)
        adj_count = 0
        for ind in adj.index:
            # adjustment details
            adj_detail = shapes.Drawing(date_box_width, date_box_height)
            r1 = shapes.Rect(date_box_x, date_box_y, date_box_width, date_box_height, fillColor=colors.white,
                             strokeColor=colors.white)
            adj_detail.add(r1)
            if adj['remarks'][ind] is None:
                description = ''
            else:
                description = adj['remarks'][ind]
            string_des = shapes.String(10, 10, description.upper(), fontName="Helvetica", fontSize=8)
            adj_detail.add(string_des)

            amt = adj['amount'][ind]
            if adj['adjustmenttype'][ind] != 2:
                if adj['crdr'][ind].lower() == 'dr':
                    amt = -1 * amt
                else:
                    amt
            else:
                amt = 0.0
            string_amt = shapes.String(260, 10, str(amt), fontName="Helvetica", fontSize=8)
            adj_detail.add(string_amt)
            totalAdjGross += amt

            amt2 = adj['amount'][ind]
            if adj['crdr'][ind].lower() == 'dr':
                amt2 = -1 * amt2
            else:
                amt2 = amt2
            string_amt2 = shapes.String(320, 10, str(amt2), fontName="Helvetica", fontSize=8)
            totalAdj += amt2
            adj_detail.add(string_amt2)

            # ($F{ADJUSTMENTTYPE} == 2) ? ($F{CRDR}.equalsIgnoreCase("CR") ? -1 * $F{AMOUNT} : $F{AMOUNT}) : 0.0
            amt3 = adj['amount'][ind]
            if adj['adjustmenttype'][ind] == 2:
                if adj['crdr'][ind].lower() == 'cr':
                    amt3 = -1 * amt3
                else:
                    amt3 = amt3
            else:
                amt3 = 0.0
            string_amt3 = shapes.String(380, 10, str(amt3), fontName="Helvetica", fontSize=8, alignX="left")
            totalAdjCommission += amt3
            adj_detail.add(string_amt3)
            fee_trandate = shapes.String(440, 10, str(adj['adjustdate'][ind])[:10], fontName="Helvetica", fontSize=8)
            adj_detail.add(fee_trandate)
            fee_trandate = shapes.String(500, 10, str(adj['adjustdate'][ind])[:10], fontName="Helvetica", fontSize=8)
            adj_detail.add(fee_trandate)
            elements.append(adj_detail)
            adj_count += 1

        if adj_count > 0:
            adj_detail2 = shapes.Drawing(date_box_width, date_box_height)
            r1 = shapes.Rect(date_box_x, date_box_y, date_box_width, date_box_height, fillColor=colors.white,
                             strokeColor=colors.white)
            adj_detail2.add(r1)
            subttl = shapes.String(10, 10, 'SUB TOTAL FOR ADJUSTMENT : ', fontName="Helvetica", fontSize=8)
            adj_detail2.add(subttl)
            # totalAdjGross
            ttlAdjGross = shapes.String(260, 10, str(totalAdjGross), fontName="Helvetica", fontSize=8)
            adj_detail2.add(ttlAdjGross)
            # totalAdj
            ttlAdj = shapes.String(320, 10, str(totalAdj), fontName="Helvetica", fontSize=8)
            adj_detail2.add(ttlAdj)
            # $V{totalAdjCommission}
            ttlAdjCommision = shapes.String(380, 10, str(totalAdjCommission), fontName="Helvetica", fontSize=8)
            adj_detail2.add(ttlAdjCommision)

            elements.append(adj_detail2)

        #######################################
        # sub report 2 (fees)
        # get data from db
        df3 = Dao.getDataforFees(df2["mid"].values[0], df1["starteodid"].values[0],
                                 df1["endeodid"].values[0])
        fees = shapes.Drawing(date_box_width, date_box_height)
        r1 = shapes.Rect(date_box_x, date_box_y, date_box_width, date_box_height, fillColor=colors.white,
                         strokeColor=colors.white)
        fees.add(r1)
        string_fees = shapes.String(10, 10, 'FEES', fontName="Helvetica", fontSize=8)
        fees.add(string_fees)
        elements.append(fees)

        fees_count = 0
        for ind in df3.index:
            # st = df3['feeamount'][ind]
            totalfee += df3['feeamount'][ind]
            # fees detail
            fees_detail = shapes.Drawing(date_box_width, date_box_height)
            r1 = shapes.Rect(date_box_x, date_box_y, date_box_width, date_box_height, fillColor=colors.white,
                             strokeColor=colors.white)
            fees_detail.add(r1)

            if df3['description'][ind] is None:
                description = ''
            else:
                description = df3['description'][ind]
            string_des = shapes.String(10, 10, description.upper(), fontName="Helvetica", fontSize=8)
            fees_detail.add(string_des)
            string_feeamnt = shapes.String(260, 10, str(df3['feeamount'][ind]), fontName="Helvetica", fontSize=8)
            fees_detail.add(string_feeamnt)
            string_feeamnt2 = shapes.String(320, 10, str(df3['feeamount'][ind]), fontName="Helvetica", fontSize=8)
            fees_detail.add(string_feeamnt2)
            string_zero = shapes.String(380, 10, '0.0', fontName="Helvetica", fontSize=8)
            fees_detail.add(string_zero)
            fee_trandate = shapes.String(440, 10, str(df3['effectdate'][ind])[:10], fontName="Helvetica", fontSize=8)
            fees_detail.add(fee_trandate)
            fee_trandate = shapes.String(500, 10, str(df3['effectdate'][ind])[:10], fontName="Helvetica", fontSize=8)
            fees_detail.add(fee_trandate)
            fees_count += 1

            elements.append(fees_detail)

        if fees_count > 0:
            fees = shapes.Drawing(date_box_width, date_box_height)
            shape = shapes.Rect(date_box_x, date_box_y, date_box_width, date_box_height, fillColor=colors.white,
                                strokeColor=colors.white)
            fees.add(shape)
            string_footeer = shapes.String(10, 10, 'SUB TOTAL FOR : FEES', fontName="Helvetica", fontSize=8)
            fees.add(string_footeer)
            string_zero = shapes.String(380, 10, '0.0', fontName="Helvetica", fontSize=8)
            fees.add(string_zero)
            string_ttlfee = shapes.String(320, 10, str(totalfee), fontName="Helvetica", fontSize=8)
            fees.add(string_ttlfee)
            string_ttlfee = shapes.String(260, 10, str(totalfee), fontName="Helvetica", fontSize=8)
            fees.add(string_ttlfee)

            elements.append(fees)

        # summery
        summery = shapes.Drawing(date_box_width, date_box_height)
        r1 = shapes.Rect(date_box_x, date_box_y, date_box_width, date_box_height, fillColor=colors.white,
                         strokeColor=colors.white)
        summery.add(r1)
        string_noofttl = shapes.String(10, 10, 'NO OF TOTAL', fontName="Helvetica-Bold",
                                       fontSize=8)
        summery.add(string_noofttl)
        # ($V{TotalGrossAdj} + $V{TotalGrossAmount} + $V{TotalFeeAdj})
        string_ttlfee = shapes.String(260, 10, str(totalAdjGross + totalfee + ttlgrossamt), fontName="Helvetica",
                                      fontSize=8)
        summery.add(string_ttlfee)

        # net amount of no of payment
        if df1["payment"].values[0] is None:
            payment = 0
        else:
            payment = df1["payment"].values[0]
        string_payment = shapes.String(320, 10, str(payment), fontName="Helvetica", fontSize=8)
        summery.add(string_payment)

        # $P{commisions}
        string_comission = shapes.String(380, 10, str(df1["commisions"].values[0]), fontName="Helvetica", fontSize=8)
        summery.add(string_comission)

        elements.append(summery)
        elements.append(herizontal_line)

        # payments section
        payments = shapes.Drawing(date_box_width, date_box_height)
        r1 = shapes.Rect(date_box_x, date_box_y, date_box_width, date_box_height, fillColor=colors.white,
                         strokeColor=colors.white)
        payments.add(r1)
        string_payments = shapes.String(10, 10, 'PAYMENTS', fontName="Helvetica-Bold", fontSize=8)
        payments.add(string_payments)
        elements.append(payments)
        elements.append(herizontal_line)

        # payment line two
        payments_line2 = shapes.Drawing(date_box_width, date_box_height)
        r1 = shapes.Rect(date_box_x, date_box_y, date_box_width, date_box_height, fillColor=colors.white,
                         strokeColor=colors.white)
        payments_line2.add(r1)
        # ($P{payment} == null) ? 0 : $P{payment}
        if df1["payment"].values[0] is None:
            payment = 0
        else:
            payment = df1["payment"].values[0]
        string_payments_l2 = shapes.String(260, 10, str(payment), fontName="Helvetica", fontSize=8)
        payments_line2.add(string_payments_l2)

        # (($P{payment} == null) || ($P{payment} == 0.0)) ? 0.0 : -$P{payment}
        if df1["payment"].values[0] is None or df1["payment"].values[0] == 0.0:
            payment = 0
        else:
            payment = -1 * df1["payment"].values[0]
        string_payments_l2 = shapes.String(320, 10, str(payment), fontName="Helvetica", fontSize=8)
        payments_line2.add(string_payments_l2)

        string_zero = shapes.String(380, 10, '0.0', fontName="Helvetica", fontSize=8)
        payments_line2.add(string_zero)
        fee_trandate = shapes.String(440, 10, str(df1["statementenddate"].values[0])[:10], fontName="Helvetica",
                                     fontSize=8)
        payments_line2.add(fee_trandate)
        fee_trandate = shapes.String(500, 10, str(df1["statementenddate"].values[0])[:10], fontName="Helvetica",
                                     fontSize=8)
        payments_line2.add(fee_trandate)

        elements.append(payments_line2)

        def addPageNumber(canvas, my_doc):
            canvas.setFont('Helvetica', 8)
            page_num = canvas.getPageNumber()
            page_no = "Page No : %s" % page_num
            canvas.drawString(10, 7, page_no)

            def addCustomString(canvas, my_doc):
                canvas.setFont('Helvetica', 8)
                custom_str = "This is a custom string"
                canvas.drawString(10, 10, custom_str)

        # build the template
        doc.build(elements, onFirstPage=addPageNumber, onLaterPages=addPageNumber)
        successcount += 1
        app.logger.info('successfully created ' + filename)
        Dao.UpdateMerchantCustomerStatementStatus(statementid)
        Dao.UpdateEodMerchantPaymentTableBillingDone(merchantid, type)

    except Exception as err:
        errorcount += 1
        app.logger.error('Error while Pdf Generating {}'.format(str(err)))

    return successcount, errorcount
