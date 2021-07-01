# Script to extract current year amounts from annual reports

# Import dependencies
import fitz
import re
import os
import csv

# Specify the folder that contains the pdf-files
inputfolder = r"File Path that contains PDF files"
# Specify the filepath of the output csv file
outputcsvfile = r"output file path.csv"


# Functions
def string_to_integer_or_float(string):
    """ This function casts a string to an integer or a float """
    if string == "-":
        return 0
    if "," in string:
        return int(string.replace(",", ""))
    else:
        return int(string)

def find_tables(source, regex):
    """ This function extracts the table from the total text, which should be concatenated """
    find_table = re.findall(regex, source, flags=re.IGNORECASE)
    if len(find_table) > 0:
        text_concat_table = find_table[0][0]
    else:
        text_concat_table = ""
    return text_concat_table

# The regex pattern defined below is used in the program to identify and extract the first and/or second number that appears after the lineitem
# pattern_integers is used to extract the first integer amount, ignores a potential note number, and checks whether there is a second amount
pattern_integers = r"\s+(?:\[[\d]+\]\s+)?([\d\,\-]+)\s+[\d\,\-]+"


# LINEITEMS
# Below for each table that will be extracted, a tuple is created.
# The first element is the name of the lineitem as it will appear in the csv file.
# The second element is the regular expression that is used by the program to find the lineitem in the table.
balance_debit_lineitems = [("Assets: Cash and cash equivalents", r"Cash\s+and\s+cash\s+equivalents"),
                           ("Assets: Financial assets at fair value through profit or loss", r"Financial\s+assets\s+at\s+fair\s+value\s+through\s+profit\s+or\s+loss"),
                           ("Assets: Outstanding transactions in financial instruments", r"Outstanding\s+transactions\s+in\s+financial\s+instruments"),
                           ("Assets: Outstanding transactions with holders of participations", r"Outstanding\s+transactions\s+with\s+holders\s+of\s+participations"),
                           ("Assets: Other assets and receivables", r"Other\s+assets\s+and\s+receivables"),
                           ("Assets: Total-assets", r"Total\-assets")
                           ]

balance_credit_lineitems = [("Liabilities: Outstanding transactions in financial instruments", r"Outstanding\s+transactions\s+in\s+financial\s+instruments"),
                            ("Liabilities: Outstanding transactions with holders of participations", r"Outstanding\s+transactions\s+with\s+holders\s+of\s+participations"),
                            ("Liabilities: Payables and other liabilities", r"Payables\s+and\s+other\s+liabilities"),
                            ("Liabilities: Total liabilities excluding net assets attributable to holders of participations", r"Total\s+liabilities\s+excluding\s+net\s+assets\s+attributable\s+to\s+holders\s+of\s+participations"),
                            ("Liabilities: Net assets attributable to holders of participations", r"\d\s+Net\s+assets\s+attributable\s+to\s+holders\s+of\s+participations"),
                            ("Liabilities: Total liabilities", r"Total\s+liabilities")
                            ]

profitloss_lineitems = [("P&L: Recognized net gains/(losses) on financial instruments at fair value through profit or loss", r"Recognized\s+net\s+gains/\(losses\)\s+on\s+financial\s+instruments\s+at\s+fair\s+value\s+through\s+profit\s+or\s+loss"),
                        ("P&L: Net interest income", r"Net\s+interest\s+income"),
                        ("P&L: Withholding tax", r"Withholding\s+tax"),
                        ("P&L: Total investment result", r"Total\s+investment\s+result"),
                        ("P&L: Subscription and redemption fee income", r"Subscription\s+and\s+redemption\s+fee\s+income"),
                        ("P&L: Other income", r"Other\s+income"),
                        ("P&L: Total other results", r"Total\s+other\s+results"),
                        ("P&L: Investment management fee", r"Investment\s+management\s+fee"),
                        ("P&L: Management fee (external)", r"Management\s+fee\s+\(external\)"),
                        ("P&L: Pricing expenses", r"Pricing\s+expenses"),
                        ("P&L: Regulatory fee", r"Regulatory\s+fee"),
                        ("P&L: Audit fee", r"Audit\s+fee"),
                        ("P&L: Depositary fee", r"Depositary\s+fee"),
                        ("P&L: Custody fee", r"Custody\s+fee"),
                        ("P&L: Other charges", r"Other\s+charges"),
                        ("P&L: Total charges", r"Total\s+charges"),
                        ("P&L: Net result attributable to holders of participations", r"Net\s+result\s+attributable\s+to\s+holders\s+of\s+participations"),
                        ("P&L: Participation Class A", r"Participation\s+Class\s+A"),
                        ("P&L: Participation Class B", r"Participation\s+Class\s+B"),
                        ("P&L: Participation Class I", r"Participation\s+Class\s+I"),
                        ("P&L: Participation Class J", r"Participation\s+Class\s+J"),
                        ("P&L: Net result attributable to holders of participations", r"Net\s+result\s+attributable\s+to\s+holders\s+of\s+participations")
                        ]

cashflow_lineitems = [("Cashflow: Purchase of financial instruments at fair value through profit or loss", r"Purchase\s+of\s+financial\s+instruments\s+at\s+fair\s+value\s+through\s+profit\s+or\s+loss"),
                      ("Cashflow: Proceeds from sale of financial instruments at fair value through profit or loss", r"Proceeds\s+from\s+sale\s+of\s+financial\s+instruments\s+at\s+fair\s+value\s+through\s+profit\s+or\s+loss"),
                      ("Cashflow: Proceeds/loss from interest", r"Proceeds/loss\s+from\s+interest"),
                      ("Cashflow: Proceeds/loss from other income", r"Proceeds/loss\s+from\s+other\s+income"),
                      ("Cashflow: Charges paid", r"Charges\s+paid"),
                      ("Cashflow: Withholding tax paid", r"Withholding\s+tax\s+paid"),
                      ("Cashflow: Net cash flow from operating activities", r"Net\s+cash\s+flow\s+from\s+operating\s+activities"),
                      ("Cashflow: Proceeds from subscriptions", r"Proceeds\s+from\s+subscriptions"),
                      ("Cashflow: Payments for redemptions", r"Payments\s+for\s+redemptions"),
                      ("Cashflow: Proceeds from subscription and redemption fee", r"Proceeds\s+from\s+subscription\s+and\s+redemption\s+fee"),
                      ("Cashflow: Net cash flow from financing activities", r"Net\s+cash\s+flow\s+from\s+financing\s+activities"),
                      ("Cashflow: Net change in cash and cash equivalents", r"Net\s+change\s+in\s+cash\s+and\s+cash\s+equivalents"),
                      ("Cashflow: Cash and cash equivalents at beginning of period", r"Cash\s+and\s+cash\s+equivalents\s+at\s+beginning\s+of\s+period"),
                      ("Cashflow: Net change in cash and cash equivalents", r"Net\s+change\s+in\s+cash\s+and\s+cash\s+equivalents"),
                      ("Cashflow: Cash and cash equivalents at end of period", r"Cash\s+and\s+cash\s+equivalents\s+at\s+end\s+of\s+period"),
                      ("Cashflow: Cash balances at banks", r"Cash\s+balances\s+at\s+banks"),
                      ("Cashflow: Balance at treasury entity", r"Balance\s+at\s+treasury\s+entity"),
                      ("Cashflow: Cash and cash equivalents", r"\d\s+Cash\s+and\s+cash\s+equivalents")
                      ]


# EXTRACT LINEITEMS AND AMOUNTS FROM PDF FILES
pdffiles = []
for filename in os.listdir(inputfolder):
    if filename.endswith("pdf"):
        pdffiles.append(filename)

funds_items = []

# loop through all the files in the inputfolder
for filename in pdffiles:

    # we use a regular expression to extract the fund name from the file name
    fundname = re.findall(r"((.*?)fund)", filename)[0][0]

    # Read in the text from the pdf and append it to the text variable
    inputfilepath = f"{inputfolder}{filename}"
    document = fitz.open(inputfilepath)

    text = ""
    for pagenumber in range(document.pageCount):
        page = document.loadPage(pagenumber)
        page_text = page.getText("text")
        text += page_text

    # Concatenate the text string, so that we can use regular expressions easily to extract the whole table
    text_concat = text.split("\n")
    text_concat = " ".join(text_concat)

    # Extract the tables using regular expressions and capture groups from the text_concat string variable
    text_concat_balance = find_tables(text_concat, r"(Statement\s+of\s+financial\s+position\s+(.*?)Statement\s+of\s+comprehensive\s+income)")
    text_concat_balance_debit = find_tables(text_concat_balance, r"(Assets(.*?)Liabilities)")
    text_concat_balance_credit = find_tables(text_concat_balance, r"(Liabilities(.+))")
    text_concat_pl = find_tables(text_concat, r"(Statement\s+of\s+comprehensive\s+income(.*?)Statement\s+of\s+Cash\s+Flows)")
    text_concat_cashflow = find_tables(text_concat, r"(Statement\s+of\s+Cash\s+Flows(.+))")


    # Create empty dictionaries for each table
    # These dictionaries will contain the extracted lineitems with the extracted numbers
    balance_sheet_debit = {}
    balance_sheet_credit = {}
    pl_account = {}
    cashflow_statement = {}


    # The list below contains tuples with objects for each table
    # The first element is the empty dictionary that will contain the lineitems and extracted numbers
    # The second element is table that contains the lineitem tuples
    # The third element is the extracted table in string format
    # The fouth element is the regex pattern that is used to extract the numbers from the tables
    # The final element specifies the position of the amount that needs to be extracted. Most often this will be a 0 for the first amount. Sometimes it will be 1 for the second amount.
    items = [(balance_sheet_debit, balance_debit_lineitems, text_concat_balance_debit, pattern_integers, 0),
             (balance_sheet_credit, balance_credit_lineitems, text_concat_balance_credit, pattern_integers, 0),
             (pl_account, profitloss_lineitems, text_concat_pl, pattern_integers, 0),
             (cashflow_statement, cashflow_lineitems, text_concat_cashflow, pattern_integers, 0)
             ]

    # Loop through the items table and through the lineitems tables, extract the correct number for each lineitem, and save it into the empty dictionaries
    for table, lineitems, text_concat_table, numbers_regex, extract_number in items:
        for lineitem_name, lineitem_regex in lineitems:
            match = re.findall(lineitem_regex + numbers_regex, text_concat_table, flags = re.I)
            if len(match) != 0:
                if type(match[0]) == str:
                    table[lineitem_name] = string_to_integer_or_float(match[extract_number])
                elif isinstance(match[0], tuple):
                    table[lineitem_name] = string_to_integer_or_float(match[0][extract_number])


    fund_items = []
    index = []

    fund_items.append(fundname)
    index.append("Fund")

    # Loop through all the line items from the line items tables and append it to the fund_items list
    for table, lineitems, text_concat_table, numbers_regex, extract_number in items:
        for lineitem_name, _ in lineitems:
            index.append(lineitem_name)
            if lineitem_name not in table:
                fund_items.append(0)
            else:
                fund_items.append(table[lineitem_name])


    funds_items.append(fund_items)

funds_items = [list(i) for i in zip(index, *funds_items)]

# Write output to a csv file
with open(outputcsvfile, "w", newline="") as f:
    writer = csv.writer(f, delimiter=";")
    for row in funds_items:
        writer.writerow(row)
