from reportlab.graphics import shapes
from app import app
from reportlab.platypus import SimpleDocTemplate, PageTemplate, Frame

import Dao
from Service import *
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


def getToBeGenerateLocationFile(eodDate):
    global statementid, merchantid, type, successno, errorno

    try:
        df = Dao.getStatementIdsForMerchantStatementFileCreation()
        successno = 0
        errorno = 0
        for ind in df.index:
            errorcount = errorno
            successcount = successno
            statementid = df['statementid'][ind]
            merchantid = df['mid'][ind]
            type = 'Location'
            successno, errorno = genarateStatementPDF(statementid, type, eodDate, merchantid, errorcount, successcount)

    except Exception as err:
        app.logger.error('Error in Merchant Statement controller {}'.format(str(err)))

    return successno, errorno


def genarateStatementPDF(statementid, type, eodDate, merchantid, errorcount, successcount):
    try:
        totalfee = 0
        totalAdjGross = 0
        totalAdj = 0
        totalAdjCommission = 0

        # get data from db
        df, df2 = Dao.getDataFromStatementID(statementid, merchantid)
        filePathDate, filepath, filename = generateFilePath(statementid, type, eodDate, merchantid)
        statementStartDate = df["statementstartdate"].values[0]
        StatementEndDate = df["statementenddate"].values[0]
        merchantDes = df["description"].values[0]

        # define page size and create a SimpleDocTemplate object
        page_size = (595, 842)
        BottomMargin = 24
        TopMargin = 4
        LeftMargin = 4
        RightMargin = 4
        doc = SimpleDocTemplate(filename, pagesize=page_size, bottomMargin=BottomMargin, topMargin=TopMargin,
                                leftMargin=LeftMargin, rightMargin=RightMargin)

        # define styles for the template
        styles = getSampleStyleSheet()

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

        # --------------------- add content -------------------------
        merchantName = shapes.String(10, 60, merchantDes, fontName="Helvetica-Bold", fontSize=10,
                                     fillColor=colors.black)
        heading_box.add(merchantName)
        # heading_box.add(report_name)
        if df["address1"].values[0] is None:
            address1 = ''
        else:
            address1 = df["address1"].values[0]
        addr1 = shapes.String(10, 45, address1, fontName="Helvetica", fontSize=8,
                              fillColor=colors.black)
        heading_box.add(addr1)
        if df["address2"].values[0] is None:
            address2 = ''
        else:
            address2 = df["address2"].values[0]
        addr2 = shapes.String(10, 35, address2, fontName="Helvetica", fontSize=8,
                              fillColor=colors.black)
        heading_box.add(addr2)
        if df["address3"].values[0] is None:
            address3 = ''
        else:
            address3 = df["address3"].values[0]
        addr3 = shapes.String(10, 25, address3, fontName="Helvetica", fontSize=8,
                              fillColor=colors.black)
        heading_box.add(addr3)
        report_name = shapes.String(130, 10, 'Transaction Detail Report From : ', fontName="Helvetica", fontSize=8)
        heading_box.add(report_name)
        date_string = str(statementStartDate)
        from_date = shapes.String(250, 10, date_string[:10], fontName="Helvetica", fontSize=8)
        heading_box.add(from_date)
        string_to = shapes.String(320, 10, 'To', fontName="Helvetica", fontSize=8)
        heading_box.add(string_to)
        date_string2 = str(StatementEndDate)
        to_date = shapes.String(350, 10, date_string2[:10], fontName="Helvetica", fontSize=8)
        heading_box.add(to_date)

        column_header_x = 0
        column_header_y = 0
        column_header_width = 580
        column_header_height = 20

        column_header = shapes.Drawing(column_header_width, column_header_height)
        r1 = shapes.Rect(column_header_x, column_header_y, column_header_width, column_header_height,
                         fillColor=colors.white,
                         strokeColor=colors.white)
        column_header.add(r1)

        # herozontal line
        herozontal_line = shapes.Drawing(580, 2)
        r1 = shapes.Rect(column_header_x, column_header_y, 580, 2,
                         fillColor=colors.black,
                         strokeColor=colors.black)
        herozontal_line.add(r1)

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

        # create the content for the template
        elements = []
        # add itemes
        elements.append(heading_box)
        elements.append(herozontal_line)
        elements.append(column_header)
        elements.append(herozontal_line)

        totalgrossamt = 0
        totalnetamt = 0
        totalcommisiion = 0

        # Create Date box drawing with rectangle
        date_box_width = 580
        date_box_height = 20
        date_box_x = 0
        date_box_y = 0

        # get data from query 2
        for ind in df2.index:
            if df2['cardassociation'][ind] == "VISA":
                global txnamt

                # merchant group header
                merchant_group_header = shapes.Drawing(date_box_width, date_box_height)
                r1 = shapes.Rect(date_box_x, date_box_y, date_box_width, date_box_height, fillColor=colors.white,
                                 strokeColor=colors.white)
                # merchant_group_header.add(r1)
                # merchant_group_string = df2['mid'][ind] + " - " + df2['merchantname'][ind]
                # string_mid = shapes.String(10, 10, merchant_group_string, fontName="Helvetica", fontSize=8)
                # merchant_group_header.add(string_mid)
                # elements.append(merchant_group_header)

                # card type group header
                if ind == 0:
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
                start_index = 6
                end_index = 11
                pattern = "*****"
                content_cardnumber = shapes.String(10, 10,
                                                   card_number[:start_index] + pattern + card_number[end_index:],
                                                   fontName="Helvetica", fontSize=8)
                detail1.add(content_cardnumber)
                string_posid = shapes.String(140, 10, df2['tid'][ind], fontName="Helvetica", fontSize=8)
                detail1.add(string_posid)
                content_auth = shapes.String(200, 10, df2['authcode'][ind], fontName="Helvetica", fontSize=8)
                detail1.add(content_auth)
                content_grossamt = shapes.String(260, 10, str(df2['transactionamount'][ind]), fontName="Helvetica",
                                                 fontSize=8)
                detail1.add(content_grossamt)
                totalgrossamt += df2['transactionamount'][ind]
                content_netamt = shapes.String(320, 10, str(df2['grossamount'][ind]), fontName="Helvetica", fontSize=8)
                totalnetamt += df2['grossamount'][ind]
                detail1.add(content_netamt)
                content_comission = shapes.String(380, 10, str(df2['merchantcommssion'][ind]), fontName="Helvetica",
                                                  fontSize=8)
                detail1.add(content_comission)
                totalcommisiion += df2['merchantcommssion'][ind]

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
        content_txn = shapes.String(260, 10, str("{:.2f}".format(totalgrossamt)), fontName="Helvetica", fontSize=8)
        card_type_footer.add(content_txn)
        if df2['totalgrossamount'][ind] is None:
            ttlgrossamt = 0.00
        else:
            ttlgrossamt = df2['totalgrossamount'][ind]
            totalnetamt
        content_ttlgrossamount = shapes.String(320, 10, str("{:.2f}".format(totalnetamt)), fontName="Helvetica",
                                               fontSize=8)
        card_type_footer.add(content_ttlgrossamount)
        content_commision = shapes.String(380, 10, str("{:.2f}".format(totalcommisiion)), fontName="Helvetica",
                                          fontSize=8)
        card_type_footer.add(content_commision)

        elements.append(card_type_footer)
        totalgrossamt = 0
        totalnetamt = 0
        totalcommisiion = 0
        master = False

        # get data for master
        for ind in df2.index:
            if df2['cardassociation'][ind] == "MASTER":
                global txnamt

                # card type group header
                if master is False:
                    card_type_header = shapes.Drawing(date_box_width, date_box_height)
                    r1 = shapes.Rect(date_box_x, date_box_y, date_box_width, date_box_height, fillColor=colors.white,
                                     strokeColor=colors.white)
                    card_type_header.add(r1)
                    string_cardassociation = shapes.String(10, 10, df2['cardassociation'][ind], fontName="Helvetica",
                                                           fontSize=8)
                    card_type_header.add(string_cardassociation)
                    elements.append(card_type_header)
                    master = True

                # detail1
                detail1 = shapes.Drawing(date_box_width, date_box_height)
                r1 = shapes.Rect(date_box_x, date_box_y, date_box_width, date_box_height, fillColor=colors.white,
                                 strokeColor=colors.white)
                detail1.add(r1)
                # --------------------- add content-------------------------
                card_number = df2['cardnumber'][ind]
                start_index = 6
                end_index = 11
                pattern = "*****"
                content_cardnumber = shapes.String(10, 10,
                                                   card_number[:start_index] + pattern + card_number[end_index:],
                                                   fontName="Helvetica", fontSize=8)
                detail1.add(content_cardnumber)
                string_posid = shapes.String(140, 10, df2['tid'][ind], fontName="Helvetica", fontSize=8)
                detail1.add(string_posid)
                content_auth = shapes.String(200, 10, df2['authcode'][ind], fontName="Helvetica", fontSize=8)
                detail1.add(content_auth)
                content_grossamt = shapes.String(260, 10, str(df2['transactionamount'][ind]), fontName="Helvetica",
                                                 fontSize=8)
                detail1.add(content_grossamt)
                totalgrossamt += df2['transactionamount'][ind]
                content_netamt = shapes.String(320, 10, str(df2['grossamount'][ind]), fontName="Helvetica", fontSize=8)
                totalnetamt += df2['grossamount'][ind]
                detail1.add(content_netamt)
                content_comission = shapes.String(380, 10, str(df2['merchantcommssion'][ind]), fontName="Helvetica",
                                                  fontSize=8)
                detail1.add(content_comission)
                totalcommisiion += df2['merchantcommssion'][ind]

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
        content_txn = shapes.String(260, 10, str("{:.2f}".format(totalgrossamt)), fontName="Helvetica", fontSize=8)
        card_type_footer.add(content_txn)
        if df2['totalgrossamount'][ind] is None:
            ttlgrossamt = 0.00
        else:
            ttlgrossamt = df2['totalgrossamount'][ind]
            totalnetamt
        content_ttlgrossamount = shapes.String(320, 10, str("{:.2f}".format(totalnetamt)), fontName="Helvetica",
                                               fontSize=8)
        card_type_footer.add(content_ttlgrossamount)
        content_commision = shapes.String(380, 10, str("{:.2f}".format(totalcommisiion)), fontName="Helvetica",
                                          fontSize=8)
        card_type_footer.add(content_commision)

        elements.append(card_type_footer)
        #########################################
        # sub report 1 (adjusment)
        adj = Dao.getSubReport1(merchantid)
        if adj.size > 0:
            adjesment = shapes.Drawing(date_box_width, date_box_height)
            r1 = shapes.Rect(date_box_x, date_box_y, date_box_width, date_box_height, fillColor=colors.white,
                             strokeColor=colors.white)
            adjesment.add(r1)
            string_fees = shapes.String(10, 10, 'ADJUSTMENT', fontName="Helvetica", fontSize=8)
            adjesment.add(string_fees)
            elements.append(adjesment)
            adj_count = 0
            for ind in adj.index:
                reportone = True
                # adjustment details
                adj_detail = shapes.Drawing(date_box_width, date_box_height)
                r1 = shapes.Rect(date_box_x, date_box_y, date_box_width, date_box_height, fillColor=colors.teal,
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
                string_amt2 = shapes.String(320, 10, str(amt2), fontName="Helvetica", fontSize=8)
                totalAdj += amt2
                adj_detail.add(string_amt2)

                # ($F{ADJUSTMENTTYPE} == 2) ? ($F{CRDR}.equalsIgnoreCase("CR") ? -1 * $F{AMOUNT} : $F{AMOUNT}) : 0.0
                amt3 = adj['amount'][ind]
                if adj['adjustmenttype'][ind] == 2:
                    if adj['crdr'][ind].lower() == 'cr':
                        amt3 = -1 * amt3
                    else:
                        amt3 = adj['amount'][ind]
                else:
                    amt3 = 0.0
                string_amt3 = shapes.String(380, 10, str(amt3), fontName="Helvetica", fontSize=8)
                totalAdjCommission += amt3
                adj_detail.add(string_amt3)
                fee_trandate = shapes.String(440, 10, str(adj['adjustdate'][ind])[:10], fontName="Helvetica",
                                             fontSize=8)
                adj_detail.add(fee_trandate)
                fee_trandate = shapes.String(500, 10, str(adj['adjustdate'][ind])[:10], fontName="Helvetica",
                                             fontSize=8)
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
        df3 = Dao.getDataToSubReportTWo(merchantid, statementStartDate, StatementEndDate)
        if df3.size > 0:
            fees = shapes.Drawing(date_box_width, date_box_height)
            r1 = shapes.Rect(date_box_x, date_box_y, date_box_width, date_box_height, fillColor=colors.white,
                             strokeColor=colors.white)
            fees.add(r1)
            string_fees = shapes.String(10, 10, 'FEES', fontName="Helvetica", fontSize=8)
            fees.add(string_fees)
            elements.append(fees)

            fees_count = 0
            for ind in df3.index:
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
                fee_trandate = shapes.String(440, 10, str(df3['effectdate'][ind])[:10], fontName="Helvetica",
                                             fontSize=8)
                fees_detail.add(fee_trandate)
                fee_trandate = shapes.String(500, 10, str(df3['effectdate'][ind])[:10], fontName="Helvetica",
                                             fontSize=8)
                fees_detail.add(fee_trandate)
                fees_count += 1

                elements.append(fees_detail)

            if fees_count > 0:
                fees_footer = shapes.Drawing(date_box_width, date_box_height)
                r1 = shapes.Rect(date_box_x, date_box_y, date_box_width, date_box_height, fillColor=colors.white,
                                 strokeColor=colors.white)
                fees_footer.add(r1)
                string_footeer = shapes.String(10, 10, 'SUB TOTAL FOR : FEES', fontName="Helvetica", fontSize=8)
                fees_footer.add(string_footeer)
                string_zero = shapes.String(380, 10, '0.0', fontName="Helvetica", fontSize=8)
                fees_footer.add(string_zero)
                string_ttlfee = shapes.String(320, 10, str(totalfee), fontName="Helvetica", fontSize=8)
                fees_footer.add(string_ttlfee)
                string_ttlfee = shapes.String(260, 10, str(totalfee), fontName="Helvetica", fontSize=8)
                fees_footer.add(string_ttlfee)

                elements.append(fees_footer)

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
        if df["payment"].values[0] is None:
            payment = 0
        else:
            payment = df["payment"].values[0]
        string_payment = shapes.String(320, 10, str(payment), fontName="Helvetica", fontSize=8)
        summery.add(string_payment)

        # $P{commisions}
        string_comission = shapes.String(380, 10, str(df["commisions"].values[0]), fontName="Helvetica", fontSize=8)
        summery.add(string_comission)

        elements.append(summery)
        elements.append(herozontal_line)

        # payments section
        payments = shapes.Drawing(date_box_width, date_box_height)
        r1 = shapes.Rect(date_box_x, date_box_y, date_box_width, date_box_height, fillColor=colors.white,
                         strokeColor=colors.white)
        payments.add(r1)
        string_payments = shapes.String(10, 10, 'PAYMENTS', fontName="Helvetica-Bold", fontSize=8)
        payments.add(string_payments)
        elements.append(payments)
        elements.append(herozontal_line)

        # payment line two
        payments_line2 = shapes.Drawing(date_box_width, date_box_height)
        r1 = shapes.Rect(date_box_x, date_box_y, date_box_width, date_box_height, fillColor=colors.white,
                         strokeColor=colors.white)
        payments_line2.add(r1)
        # ($P{payment} == null) ? 0 : $P{payment}
        if df["payment"].values[0] is None:
            payment = 0
        else:
            payment = df["payment"].values[0]
        string_payments_l2 = shapes.String(260, 10, str(payment), fontName="Helvetica", fontSize=8)
        payments_line2.add(string_payments_l2)

        # (($P{payment} == null) || ($P{payment} == 0.0)) ? 0.0 : -$P{payment}
        if df["payment"].values[0] is None or df["payment"].values[0] == 0.0:
            payment = 0
        else:
            payment = -1 * df["payment"].values[0]
        string_payments_l2 = shapes.String(320, 10, str(payment), fontName="Helvetica", fontSize=8)
        payments_line2.add(string_payments_l2)

        string_zero = shapes.String(380, 10, '0.0', fontName="Helvetica", fontSize=8)
        payments_line2.add(string_zero)
        fee_trandate = shapes.String(440, 10, str(StatementEndDate)[:10], fontName="Helvetica", fontSize=8)
        payments_line2.add(fee_trandate)
        fee_trandate = shapes.String(500, 10, str(StatementEndDate)[:10], fontName="Helvetica", fontSize=8)
        payments_line2.add(fee_trandate)

        elements.append(payments_line2)
        elements.append(herozontal_line)

        # spacer
        spacer_box_x = 0
        spacer_box_y = -1
        spacer_box_width = 580
        spacer_box_height = 20

        spacer_box = shapes.Drawing(spacer_box_width, spacer_box_height)
        spacer = shapes.Rect(spacer_box_x, spacer_box_y, spacer_box_width, spacer_box_height, fillColor=colors.black,
                             strokeColor=colors.white)
        spacer_box.add(spacer)

        def addPageNumber(canvas, my_doc):
            canvas.setFont('Helvetica', 8)

            page_num = canvas.getPageNumber()
            page_no = "Page No : %s" % page_num
            canvas.drawString(10, 7, page_no)

        # build the template
        doc.build(elements, onFirstPage=addPageNumber, onLaterPages=addPageNumber)
        app.logger.info('successfully created ' + filename)

        successcount += 1
        Dao.UpdateMerchantStatementStatus(statementid)
        Dao.UpdateEodMerchantPaymentTableBillingDone(merchantid, type)

    except Exception as err:
        errorcount += 1
        app.logger.error('Error while Pdf generating {}'.format(str(err)))

    return successcount, errorcount
