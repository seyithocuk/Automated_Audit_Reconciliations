
# Script to extract current year amounts from annual reports


# import dependencies
import fitz
import re
import os
import csv

# Specify the folder that contains the pdf-files
inputfolder = r"File Path that contains PDF files"
# Specify the filepath of the output csv file
outputcsvfile = r"output file path.csv"


def string_to_integer_or_float(string):
    """ This function casts a string to an integer or a float """
    if string == "-":
        return 0
    if "," in string or "%" in string:
        return float(string.replace(".", "").replace(",",".").replace("%", ""))
    elif "." in string:
        return int(string.replace(".", ""))
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

# The regex patterns defined below are used in the program to identify and extract the first and/or second number that appears after the lineitem 
# pattern_integers is used to extract the first integer amount, ignores a potential note number, and checks whether there is a second amount
pattern_integers = r"\s+(?:\[[\d]+\]\s+)?([\d\.\-]+)\s+[\d\.\-]+"
# pattern_portfolio is used to extract both the first integer amount and the second percentage amount
pattern_portfolio = r"\s+([\d\.\-]+)\s+([\d\,\-]+)\s+[\d\.\-]+\s+[\d\,\-]+"
# pattern_integerfloat is used to extract the first amount, which could be an integer or a float (for example a percentage), and checks whether there is a second amount
pattern_integerfloat = r"\s+([\d\.\,\-%]+)\s+[\d\.\,\-%]+"


# LINEITEMS
# Below for each table that will be extracted, a tuple is created. 
# The first element is the name of the lineitem as it will appear in the csv file. 
# The second element is the regular expression that is used by the program to find the lineitem in the table.


balance_debit_lineitems = [("BalansDebit: Aandelen en aandelenfondsen", r"Aandelen\s+en\s+aandelenfondsen"),
                           ("BalansDebit: Obligaties en obligatiefondsen", r"Obligaties\s+en\s+obligatiefondsen"),
                           ("BalansDebit: Onroerend goed (fondsen)", r"Onroerend\s+goed\s+\(?fondsen\)?"),
                           ("BalansDebit: Vastgoed (fondsen)", r"Vastgoed\s+\(?fondsen\)?"),
                           ("BalansDebit: Geldmarktfondsen", r"Geldmarktfondsen"),
                           ("BalansDebit: Hypothekenfondsen", r"Hypothekenfondsen"),
                           ("BalansDebit: Aandelenfutures", r"Aandelenfutures"),
                           ("BalansDebit: Obligatiefutures", r"Obligatiefutures"),
                           ("BalansDebit: Commodityfutures", r"Commodityfutures"),
                           ("BalansDebit: Valutafutures", r"Valutafutures"),
                           ("BalansDebit: Valutatermijncontracten", r"Valutatermijncontracten"),
                           ("BalansDebit: Totaal beleggingen", r"Totaal\s+beleggingen"),
                           ("BalansDebit: Vorderingen uit hoofde van beleggingsactiviteiten", r"(?:Vorderingen\s+uit\s+hoofde\s+van\s*beleggingsactiviteiten|beleggingsactiviteiten)"),
                           ("BalansDebit: Vorderingen uit hoofde van beleggingstransacties", r"(?:Vorderingen\s+uit\s+hoofde\s+van\s*beleggingstransacties|beleggingstransacties)"),
                           ("BalansDebit: Vorderingen uit hoofde van uitgifte participaties", r"(?:Vorderingen\s+uit\s+hoofde\s+van\s*uitgifte\s+participaties|uitgifte\s+participaties)"),
                           ("BalansDebit: Overige vorderingen", r"Overige\s+vorderingen"),
                           ("BalansDebit: Totaal vorderingen", r"Totaal\s+vorderingen"),
                           ("BalansDebit: Liquide middelen", r"Liquide\s+middelen"),
                           ("BalansDebit: Totaal activa", r"Totaal\s+activa")
                           ]


balance_credit_lineitems = [("BalansCredit: Fondsvermogen participanten", r"Fondsvermogen\s+participanten"),
                            ("BalansCredit: Aandelen en aandelenfondsen", r"Aandelen\s+en\s+aandelenfondsen"),
                            ("BalansCredit: Obligaties en obligatiefondsen", r"Obligaties\s+en\s+obligatiefondsen"),
                            ("BalansCredit: Onroerend goed (fondsen)", r"Onroerend\s+goed\s+\(?fondsen\)?"),
                            ("BalansCredit: Aandelenfutures", r"Aandelenfutures"),
                            ("BalansCredit: Obligatiefutures", r"Obligatiefutures"),
                            ("BalansCredit: Commodityfutures", r"Commodityfutures"),
                            ("BalansCredit: Valutafutures", r"Valutafutures"),
                            ("BalansCredit: Valutatermijncontracten", r"Valutatermijncontracten"),
                            ("BalansCredit: Totaal beleggingen", r"Totaal\s+beleggingen"),
                            ("BalansCredit: Schulden uit hoofde van beleggingsactiviteiten", r"(?:Schulden\s+uit\s+hoofde\s+van\s*beleggingsactiviteiten|beleggingsactiviteiten)"),
                            ("BalansCredit: Schulden uit hoofde van beleggingstransacties", r"(?:Schulden\s+uit\s+hoofde\s+van\s*beleggingstransacties|beleggingstransacties)"),
                            ("BalansCredit: Schulden uit hoofde van inname participaties", r"(?:Schulden\s+uit\s+hoofde\s+van\s+inname\s+participaties|inname\s+participaties)"),
                            ("BalansCredit: Overige schulden", r"Overige\s+schulden"),
                            ("BalansCredit: Totaal kortlopende schulden", r"Totaal\s+kortlopende\s+schulden"),
                            ("BalansCredit: Totaal passiva", r"Totaal\s+passiva")
                            ]


profitloss_lineitems = [("P&L: Dividenden", r"Dividenden"),
                        ("P&L: Interest", r"Interest"),
                        ("P&L: Overige opbrengsten", r"Overige\s+opbrengsten"),
                        ("P&L: Direct beleggingsresultaat", r"\s+Direct\s+beleggingsresultaat"),
                        ("P&L: Waardeveranderingen van beleggingen", r"Waardeveranderingen\s+van\s+beleggingen"),
                        ("P&L: Indirect beleggingsresultaat", r"Indirect\s+beleggingsresultaat"),
                        ("P&L: Totaal beleggingsresultaat", r"Totaal\s+beleggingsresultaat"),
                        ("P&L: Toe- en uittredingsvergoedingen", r"Toe\-?\s*en\s+uittredingsvergoedingen"),
                        ("P&L: Securities lending", r"Securities\s*lending"),
                        ("P&L: Kosten inlenen aandelen", r"Kosten\s+inlenen\s+aandelen"),
                        ("P&L: Koersresultaten op valutaomrekening", r"Koersresultaten\s+op\s+valutaomrekening"),
                        ("P&L: Directed brokerage", r"Directed\s+brokerage"),
                        ("P&L: Overige resultaten", r"Overige\s+resultaten"),
                        ("P&L: Totaal overig resultaat", r"Totaal\s+overig\s+resultaat"),
                        ("P&L: Beheervergoeding", r"Beheervergoeding"),
                        ("P&L: Bewaarvergoeding", r"Bewaarvergoeding"),
                        ("P&L: Accountantskosten", r"Accountantskosten"),
                        ("P&L: Juridische kosten", r"Juridische\s+kosten"),
                        ("P&L: Administratie- en bankkosten", r"Administratie\-?\s*en\s+bankkosten"),
                        ("P&L: Koerskosten", r"Koerskosten"),
                        ("P&L: Kosten toezichthouders", r"Kosten\s+toezichthouders"),
                        ("P&L: Depositary Fee", r"Depositary\s+Fee"),
                        ("P&L: Regulatory Fee", r"Regulatory\s+Fee"),
                        ("P&L: Pricing kosten", r"Pricing(?:\s+kosten|\s+expenses)"),
                        ("P&L: Benchmark kosten", r"Benchmark\s+kosten"),
                        ("P&L: Overige kosten", r"Overige\s+kosten"),
                        ("P&L: Som van de kosten", r"Som\s+van\s+de\s+kosten"),
                        ("P&L: Totaal resultaat", r"Totaal\s+resultaat")
                        ]

cashflow_lineitems = [("Kasstroomoverzicht: Ontvangsten uit hoofde van dividenden", r"Ontvangsten\s+uit\s+hoofde\s+van\s+dividenden"),
                      ("Kasstroomoverzicht: Ontvangsten uit hoofde van dividenden en belastingen", r"Ontvangsten\s+uit\s+hoofde\s+van\s+dividenden\s+en\s+belastingen"),
                      ("Kasstroomoverzicht: Ontvangsten uit hoofde van interest", r"Ontvangsten\s+uit\s+hoofde\s+van\s+interest"),
                      ("Kasstroomoverzicht: Ontvangsten uit hoofde van interest en belastingen", r"Ontvangsten\s+uit\s+hoofde\s+van\s+interest\s+en\s+belastingen"),
                      ("Kasstroomoverzicht: Ontvangsten uit hoofde van overige resultaten", r"Ontvangsten\s+uit\s+hoofde\s+van\s+overige\s+resultaten"),
                      ("Kasstroomoverzicht: Ontvangsten en uitgaven uit hoofde van interest", r"(?:Ontvangsten\s+en\s+uitgaven\s+uit\s+hoofde\s+van\s+interest|Ontvangsten\/uitgaven\s+uit\s+hoofde\s+van\s+interest)"),
                      ("Kasstroomoverzicht: Ontvangsten en uitgaven uit hoofde van overige resultaten", r"(?:Ontvangsten\s+en\s+uitgaven\s+uit\s+hoofde\s+van\s+overige\s+resultaten|Ontvangsten\/uitgaven\s+uit\s+hoofde\s+van\s+overige\s+resultaten)"),
                      ("Kasstroomoverzicht: Uitgaven uit hoofde van overige resultaten", r"\s+Uitgaven\s+uit\s+hoofde\s+van\s+overige\s+resultaten"),
                      ("Kasstroomoverzicht: Uitgaven en verrekeningen inzake kosten", r"Uitgaven\s+en\s+verrekeningen\s+inzake\s+kosten"),
                      ("Kasstroomoverzicht: Betalingen uit hoofde van interest", r"Betalingen\s+uit\s+hoofde\s+van\s+interest"),
                      ("Kasstroomoverzicht: Securities lending", r"Securities\s+lending"),
                      ("Kasstroomoverzicht: Aankopen van beleggingen", r"Aankopen\s+van\s+beleggingen"),
                      ("Kasstroomoverzicht: Verkopen van beleggingen", r"Verkopen\s+van\s+beleggingen"),
                      ("Kasstroomoverzicht: Afwikkeling valutatermijncontracten", r"Afwikkeling\s+valutatermijncontracten"),
                      ("Kasstroomoverzicht: Mutatie marginverplichtingen", r"Mutatie\s+marginverplichtingen"),
                      ("Kasstroomoverzicht: Mutatie cash collateral", r"Mutatie\s+cash\s+collateral"),
                      ("Kasstroomoverzicht: Totaal kasstroom uit beleggingsactiviteiten", r"Totaal\s+kasstroom\s+uit\s+beleggingsactiviteiten"),
                      ("Kasstroomoverzicht: Ontvangsten bij uitgifte participaties", r"Ontvangsten\s+bij\s+uitgifte\s+participaties"),
                      ("Kasstroomoverzicht: Betaald bij inkoop participaties", r"Betaald\s+bij\s+inkoop\s+participaties"),
                      ("Kasstroomoverzicht: Toe- en uittredingsvergoedingen", r"Toe\-\s*en\s+uittredingsvergoedingen"),
                      ("Kasstroomoverzicht: Transfer liquide middelen", r"Transfer\s+liquide\s+middelen"),
                      ("Kasstroomoverzicht: Terugstorting kapitaal", r"Terugstorting\s+kapitaal"),
                      ("Kasstroomoverzicht: Totaal kasstroom uit financieringsactiviteiten", r"Totaal\s+kasstroom\s+uit\s+financieringsactiviteiten"),
                      ("Kasstroomoverzicht: Netto kasstroom", r"Netto\s+kasstroom"),
                      ("Kasstroomoverzicht: Koers- en omrekeningsverschillen", r"Koers\-\s*en\s+omrekeningsverschillen"),
                      ("Kasstroomoverzicht: Koers- en omrekeningsverschillen op liquide middelen", r"Koers\-\s*en\s+omrekeningsverschillen\s+op\s+liquide\s+middelen"),
                      ("Kasstroomoverzicht: Liquide middelen begin boekjaar", r"Liquide\s+middelen\s+begin\s+boekjaar"),
                      ("Kasstroomoverzicht: Liquide middelen einde boekjaar", r"Liquide\s+middelen\s+einde\s+boekjaar"),
                      ("Kasstroomoverzicht: Mutatie liquide middelen", r"Mutatie\s+liquide\s+middelen"),
                      ("Kasstroomoverzicht: Banktegoeden", r"Banktegoeden"),
                      ("Kasstroomoverzicht: Schulden aan kredietinstellingen", r"Schulden\s+aan\s+kredietinstellingen"),
                      ("Kasstroomoverzicht: Rekening-courant Stichting TKP Pensioen Treasury", r"Rekening\-courant\s+Stichting\s+TKP\s+Pensioen\s+Treasury"),
                      ("Kasstroomoverzicht: Totaal liquide middelen", r"Totaal\s+liquide\s+middelen")
                      ]

toelichting_aandelen_lineitems = [("Note. Aandelen en aandelenfondsen / Mutatieoverzicht aandelen en aandelenfondsen: Marktwaarde begin boekjaar", r"Marktwaarde\s+begin\s+boekjaar"),
                                  ("Note. Aandelen en aandelenfondsen / Mutatieoverzicht aandelen en aandelenfondsen: Aankopen", r"Aankopen"),
                                  ("Note. Aandelen en aandelenfondsen / Mutatieoverzicht aandelen en aandelenfondsen: Verkopen", r"Verkopen"),
                                  ("Note. Aandelen en aandelenfondsen / Mutatieoverzicht aandelen en aandelenfondsen: Verkopen en aflossingen", r"Verkopen\s+en\s+aflossingen"),
                                  ("Note. Aandelen en aandelenfondsen / Mutatieoverzicht aandelen en aandelenfondsen: Overdracht van stukken", r"Overdracht\s+van\s+stukken"),
                                  ("Note. Aandelen en aandelenfondsen / Mutatieoverzicht aandelen en aandelenfondsen: Waardeveranderingen", r"Waardeveranderingen"),
                                  ("Note. Aandelen en aandelenfondsen / Mutatieoverzicht aandelen en aandelenfondsen: Marktwaarde einde boekjaar", r"Marktwaarde\s+einde\s+boekjaar")
                                  ]

toelichting_obligaties_lineitems = [("Note. Obligaties en obligatiefondsen / Mutatieoverzicht obligaties en obligatiefondsen: Marktwaarde begin boekjaar", r"Marktwaarde\s+begin\s+boekjaar"),
                                    ("Note. Obligaties en obligatiefondsen / Mutatieoverzicht obligaties en obligatiefondsen: Aankopen", r"Aankopen"),
                                    ("Note. Obligaties en obligatiefondsen / Mutatieoverzicht obligaties en obligatiefondsen: Verkopen", r"Verkopen"),
                                    ("Note. Obligaties en obligatiefondsen / Mutatieoverzicht obligaties en obligatiefondsen: Verkopen en aflossingen", r"Verkopen\s+en\s+aflossingen"),
                                    ("Note. Obligaties en obligatiefondsen / Mutatieoverzicht obligaties en obligatiefondsen: Overdracht van stukken", r"Overdracht\s+van\s+stukken"),
                                    ("Note. Obligaties en obligatiefondsen / Mutatieoverzicht obligaties en obligatiefondsen: Waardeveranderingen", r"Waardeveranderingen"),
                                    ("Note. Obligaties en obligatiefondsen / Mutatieoverzicht obligaties en obligatiefondsen: Marktwaarde einde boekjaar", r"Marktwaarde\s+einde\s+boekjaar")
                                    ]

toelichting_onroerend_lineitems = [("Note. Onroerend goed (fondsen) / Mutatieoverzicht onroerend goed (fondsen): Marktwaarde begin boekjaar", r"Marktwaarde\s+begin\s+boekjaar"),
                                   ("Note. Onroerend goed (fondsen) / Mutatieoverzicht onroerend goed (fondsen): Aankopen", r"Aankopen"),
                                   ("Note. Onroerend goed (fondsen) / Mutatieoverzicht onroerend goed (fondsen): Verkopen", r"Verkopen"),
                                   ("Note. Onroerend goed (fondsen) / Mutatieoverzicht onroerend goed (fondsen): Verkopen en aflossingen", r"Verkopen\s+en\s+aflossingen"),
                                   ("Note. Onroerend goed (fondsen) / Mutatieoverzicht onroerend goed (fondsen): Overdracht van stukken", r"Overdracht\s+van\s+stukken"),
                                   ("Note. Onroerend goed (fondsen) / Mutatieoverzicht onroerend goed (fondsen): Waardeveranderingen", r"Waardeveranderingen"),
                                   ("Note. Onroerend goed (fondsen) / Mutatieoverzicht onroerend goed (fondsen): Marktwaarde einde boekjaar", r"Marktwaarde\s+einde\s+boekjaar")
                                   ]

toelichting_aandelenfutures_lineitems = [("Note. Aandelenfutures / Mutatieoverzicht aandelenfutures: Marktwaarde begin boekjaar", r"Marktwaarde\s+begin\s+boekjaar"),
                                         ("Note. Aandelenfutures / Mutatieoverzicht aandelenfutures: Aankopen", r"Aankopen"),
                                         ("Note. Aandelenfutures / Mutatieoverzicht aandelenfutures: Verkopen", r"Verkopen"),
                                         ("Note. Aandelenfutures / Mutatieoverzicht aandelenfutures: Verkopen en aflossingen", r"Verkopen\s+en\s+aflossingen"),
                                         ("Note. Aandelenfutures / Mutatieoverzicht aandelenfutures: Overdracht van stukken", r"Overdracht\s+van\s+stukken"),
                                         ("Note. Aandelenfutures / Mutatieoverzicht aandelenfutures: Waardeveranderingen", r"Waardeveranderingen"),
                                         ("Note. Aandelenfutures / Mutatieoverzicht aandelenfutures: Marktwaarde einde boekjaar", r"Marktwaarde\s+einde\s+boekjaar")
                                         ]

toelichting_valutatermijncontracten_lineitems = [("Note. Valutatermijncontracten / Mutatieoverzicht valutatermijncontracten: Marktwaarde begin boekjaar", r"Marktwaarde\s+begin\s+boekjaar"),
                                                 ("Note. Valutatermijncontracten / Mutatieoverzicht valutatermijncontracten: Aankopen", r"Aankopen"),
                                                 ("Note. Valutatermijncontracten / Mutatieoverzicht valutatermijncontracten: Verkopen", r"Verkopen"),
                                                 ("Note. Valutatermijncontracten / Mutatieoverzicht valutatermijncontracten: Verkopen en aflossingen", r"Verkopen\s+en\s+aflossingen"),
                                                 ("Note. Valutatermijncontracten / Mutatieoverzicht valutatermijncontracten: Overdracht van stukken", r"Overdracht\s+van\s+stukken"),
                                                 ("Note. Valutatermijncontracten / Mutatieoverzicht valutatermijncontracten: Verkopen en expiraties", r"Verkopen\s+en\s+expiraties"),
                                                 ("Note. Valutatermijncontracten / Mutatieoverzicht valutatermijncontracten: Waardeveranderingen", r"Waardeveranderingen"),
                                                 ("Note. Valutatermijncontracten / Mutatieoverzicht valutatermijncontracten: Marktwaarde einde boekjaar", r"Marktwaarde\s+einde\s+boekjaar")
                                                 ]

toelichting_vastgoed_lineitems = [("Note. Vastgoed (fondsen) / Mutatieoverzicht vastgoed (fondsen): Marktwaarde begin boekjaar", r"Marktwaarde\s+begin\s+boekjaar"),
                                  ("Note. Vastgoed (fondsen) / Mutatieoverzicht vastgoed (fondsen): Aankopen", r"Aankopen"),
                                  ("Note. Vastgoed (fondsen) / Mutatieoverzicht vastgoed (fondsen): Verkopen", r"Verkopen"),
                                  ("Note. Vastgoed (fondsen) / Mutatieoverzicht vastgoed (fondsen): Verkopen en aflossingen", r"Verkopen\s+en\s+aflossingen"),
                                  ("Note. Vastgoed (fondsen) / Mutatieoverzicht vastgoed (fondsen): Overdracht van stukken", r"Overdracht\s+van\s+stukken"),
                                  ("Note. Vastgoed (fondsen) / Mutatieoverzicht vastgoed (fondsen): Waardeveranderingen", r"Waardeveranderingen"),
                                  ("Note. Vastgoed (fondsen) / Mutatieoverzicht vastgoed (fondsen): Marktwaarde einde boekjaar", r"Marktwaarde\s+einde\s+boekjaar")
                                  ]

toelichting_geldmarktfondsen_lineitems = [("Note. Geldmarktfondsen / Mutatieoverzicht geldmarktfondsen: Marktwaarde begin boekjaar", r"Marktwaarde\s+begin\s+boekjaar"),
                                          ("Note. Geldmarktfondsen / Mutatieoverzicht geldmarktfondsen: Aankopen", r"Aankopen"),
                                          ("Note. Geldmarktfondsen / Mutatieoverzicht geldmarktfondsen: Verkopen", r"Verkopen"),
                                          ("Note. Geldmarktfondsen / Mutatieoverzicht geldmarktfondsen: Verkopen en aflossingen", r"Verkopen\s+en\s+aflossingen"),
                                          ("Note. Geldmarktfondsen / Mutatieoverzicht geldmarktfondsen: Overdracht van stukken", r"Overdracht\s+van\s+stukken"),
                                          ("Note. Geldmarktfondsen / Mutatieoverzicht geldmarktfondsen: Waardeveranderingen", r"Waardeveranderingen"),
                                          ("Note. Geldmarktfondsen / Mutatieoverzicht geldmarktfondsen: Marktwaarde einde boekjaar", r"Marktwaarde\s+einde\s+boekjaar")
                                          ]

toelichting_hypotheekfondsen_lineitems = [("Note. Hypotheekfondsen / Mutatieoverzicht hypotheekfondsen: Marktwaarde begin boekjaar", r"Marktwaarde\s+begin\s+boekjaar"),
                                          ("Note. Hypotheekfondsen / Mutatieoverzicht hypotheekfondsen: Aankopen", r"Aankopen"),
                                          ("Note. Hypotheekfondsen / Mutatieoverzicht hypotheekfondsen: Verkopen", r"Verkopen"),
                                          ("Note. Hypotheekfondsen / Mutatieoverzicht hypotheekfondsen: Verkopen en aflossingen", r"Verkopen\s+en\s+aflossingen"),
                                          ("Note. Hypotheekfondsen / Mutatieoverzicht hypotheekfondsen: Overdracht van stukken", r"Overdracht\s+van\s+stukken"),
                                          ("Note. Hypotheekfondsen / Mutatieoverzicht hypotheekfondsen: Waardeveranderingen", r"Waardeveranderingen"),
                                          ("Note. Hypotheekfondsen / Mutatieoverzicht hypotheekfondsen: Marktwaarde einde boekjaar", r"Marktwaarde\s+einde\s+boekjaar")
                                          ]

countries_amounts = [("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Nederland", r"Nederland"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Verenigd Koninkrijk", r"Verenigd\s+Koninkrijk"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Luxemburg", r"Luxemburg"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Frankrijk", r"Frankrijk"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Duitsland", r"Duitsland"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: India", r"India"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Spanje", r"Spanje"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Ierland", r"Ierland"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Italië", r"Italië"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Verenigde Staten", r"Verenigde\s+Staten"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Portugal", r"Portugal"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Oostenrijk", r"Oostenrijk"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Finland", r"Finland"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Australië", r"Australië"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Zweden", r"Zweden"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Zwitserland", r"Zwitserland"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Noorwegen", r"Noorwegen"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Denemarken", r"Denemarken"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: België", r"België"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Japan", r"Japan"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Mexico", r"Mexico"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Indonesië", r"Indonesië"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Oekraïne", r"Oekraïne"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Egypte", r"Egypte"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Turkije", r"Turkije"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Qatar", r"Qatar"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Costa Rica", r"Costa\s+Rica"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Azerbeidzjan", r"Azerbeidzjan"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Argentinië", r"Argentinië"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Panama", r"Panama"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Brazilië", r"Brazilië"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Sri Lanka", r"Sri\s+Lanka"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Ecuador", r"Ecuador"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Dominicaanse Republiek", r"Dominicaanse\s+Republiek"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Kroatië", r"Kroatië"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: China", r"China"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Taiwan", r"Taiwan"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Zuid-Korea", r"Zuid\s*\-?\s*Korea"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Hongkong", r"Hongkong"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Zuid-Afrika", r"Zuid\s*\-?\s*Africa"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Chili", r"Chili"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Rusland", r"Rusland"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Singapore", r"Singapore"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Filipijnen", r"Filipijnen"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Verenigde Arabische Emiraten", r"Verenigde\s+Arabische\s+Emiraten"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Canada", r"Canada"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Israïl", r"Israïl"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Mix", r"Mix"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Overige", r"Overige"),
                     ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Bedrag: Overig", r"Overig")
                     ]

countries_percentages = [("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Nederland", r"Nederland"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Verenigd Koninkrijk", r"Verenigd\s+Koninkrijk"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Luxemburg", r"Luxemburg"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Frankrijk", r"Frankrijk"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Duitsland", r"Duitsland"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: India", r"India"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Spanje", r"Spanje"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Ierland", r"Ierland"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Italië", r"Italië"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Verenigde Staten", r"Verenigde\s+Staten"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Portugal", r"Portugal"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Oostenrijk", r"Oostenrijk"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Finland", r"Finland"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Australië", r"Australië"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Zweden", r"Zweden"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Zwitserland", r"Zwitserland"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Noorwegen", r"Noorwegen"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Denemarken", r"Denemarken"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: België", r"België"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Japan", r"Japan"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Mexico", r"Mexico"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Indonesië", r"Indonesië"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Oekraïne", r"Oekraïne"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Egypte", r"Egypte"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Turkije", r"Turkije"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Qatar", r"Qatar"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Costa Rica", r"Costa\s+Rica"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Azerbeidzjan", r"Azerbeidzjan"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Argentinië", r"Argentinië"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Panama", r"Panama"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Brazilië", r"Brazilië"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Sri Lanka", r"Sri\s+Lanka"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Ecuador", r"Ecuador"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Dominicaanse Republiek", r"Dominicaanse\s+Republiek"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Kroatië", r"Kroatië"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: China", r"China"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Taiwan", r"Taiwan"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Zuid-Korea", r"Zuid\s*\-?\s*Korea"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Hongkong", r"Hongkong"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Zuid-Afrika", r"Zuid\s*\-?\s*Africa"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Chili", r"Chili"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Rusland", r"Rusland"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Singapore", r"Singapore"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Filipijnen", r"Filipijnen"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Verenigde Arabische Emiraten", r"Verenigde\s+Arabische\s+Emiraten"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Canada", r"Canada"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Israïl", r"Israïl"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Mix", r"Mix"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Overige", r"Overige"),
                         ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar land Percentage: Overig", r"Overig")
                         ]


industries_amounts = [("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Bedrag: Hypotheken", r"Hypotheken"),
                      ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Bedrag: Consumentenleningen", r"Consumentenleningen"),
                      ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Bedrag: Autoleningen", r"Autoleningen"),
                      ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Bedrag: Woningen", r"Woningen"),
                      ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Bedrag: Hotels", r"Hotels"),
                      ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Bedrag: Kantoren", r"Kantoren"),
                      ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Bedrag: Winkels", r"Winkels"),
                      ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Bedrag: Bedrijfsleningen", r"Bedrijfsleningen"),
                      ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Bedrag: Commercieel Vastgoed", r"Commercieel\s+Vastgoed"),
                      ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Bedrag: Studentenleningen", r"Studentenleningen"),
                      ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Bedrag: Staatsobligaties", r"Staatsobligaties"),
                      ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Bedrag: Financiële instellingen", r"Financiële\s+instellingen"),
                      ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Bedrag: Niet-duurzame consumentengoederen", r"Niet\-duurzame\s+consumentengoederen"),
                      ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Bedrag: Nutsbedrijven", r"Nutsbedrijven"),
                      ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Bedrag: Telecommunicatie", r"Telecommunicatie"),
                      ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Bedrag: Duurzame consumentengoederen", r"\s+Duurzame\s+consumentengoederen"),
                      ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Bedrag: Industrie", r"Industrie"),
                      ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Bedrag: Energie", r"Energie"),
                      ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Bedrag: Informatie technologie", r"Informatie\s+technologie"),
                      ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Bedrag: Basismaterialen", r"Basismaterialen"),
                      ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Bedrag: Overheid", r"Overheid"),
                      ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Bedrag: Gezondheidszorg", r"Gezondheidszorg"),
                      ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Bedrag: Onroerend goed", r"Onroerend\+goed"),
                      ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Bedrag: REITs Gediversificeerd vastgoed", r"Ts\s+Gediversificeerds+vastgoed"),
                      ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Bedrag: REITs Winkels vastgoed", r"REITs\s+Winkels\s+vastgoed"),
                      ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Bedrag: REITs Kantoren vastgoed", r"REITs\s+Kantoren\s+vastgoed"),
                      ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Bedrag: Non REITs vastgoed", r"Non\s+REITs\s+vastgoed"),
                      ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Bedrag: REITs Woningen vastgoed", r"REITs\s+Woningen\s+vastgoed"),
                      ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Bedrag: REITs Industrieel vastgoed", r"REITs\s+Industrieel\s+vastgoed"),
                      ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Bedrag: Gezondheidszorg gerelateerd vastgoed", r"Gezondheidszorg\s+gerelateerd\s+vastgoed"),
                      ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Bedrag: REITs Overig", r"REITs\s+Overig"),
                      ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Bedrag: Overige", r"Overige"),
                      ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Bedrag: Overig", r"Overig")
                      ]

industries_percentages = [("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Percentage: Hypotheken", r"Hypotheken"),
                          ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Percentage: Consumentenleningen", r"Consumentenleningen"),
                          ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Percentage: Autoleningen", r"Autoleningen"),
                          ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Percentage: Woningen", r"Woningen"),
                          ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Percentage: Hotels", r"Hotels"),
                          ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Percentage: Kantoren", r"Kantoren"),
                          ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Percentage: Winkels", r"Winkels"),
                          ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Percentage: Bedrijfsleningen", r"Bedrijfsleningen"),
                          ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Percentage: Commercieel Vastgoed", r"Commercieel\s+Vastgoed"),
                          ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Percentage: Studentenleningen", r"Studentenleningen"),
                          ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Percentage: Staatsobligaties", r"Staatsobligaties"),
                          ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Percentage: Financiële instellingen", r"Financiële\s+instellingen"),
                          ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Percentage: Niet-duurzame consumentengoederen", r"Niet\-duurzame\s+consumentengoederen"),
                          ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Percentage: Nutsbedrijven", r"Nutsbedrijven"),
                          ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Percentage: Telecommunicatie", r"Telecommunicatie"),
                          ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Percentage: Duurzame consumentengoederen", r"\s+Duurzame\s+consumentengoederen"),
                          ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Percentage: Industrie", r"Industrie"),
                          ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Percentage: Energie", r"Energie"),
                          ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Percentage: Informatie technologie", r"Informatie\s+technologie"),
                          ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Percentage: Basismaterialen", r"Basismaterialen"),
                          ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Percentage: Overheid", r"Overheid"),
                          ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Percentage: Gezondheidszorg", r"Gezondheidszorg"),
                          ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Percentage: Onroerend goed", r"Onroerend\+goed"),
                          ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Percentage: REITs Gediversificeerd vastgoed", r"Ts\s+Gediversificeerds+vastgoed"),
                          ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Percentage: REITs Winkels vastgoed", r"REITs\s+Winkels\s+vastgoed"),
                          ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Percentage: REITs Kantoren vastgoed", r"REITs\s+Kantoren\s+vastgoed"),
                          ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Percentage: Non REITs vastgoed", r"Non\s+REITs\s+vastgoed"),
                          ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Percentage: REITs Woningen vastgoed", r"REITs\s+Woningen\s+vastgoed"),
                          ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Percentage: REITs Industrieel vastgoed", r"REITs\s+Industrieel\s+vastgoed"),
                          ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Percentage: Gezondheidszorg gerelateerd vastgoed", r"Gezondheidszorg\s+gerelateerd\s+vastgoed"),
                          ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Percentage: REITs Overig", r"REITs\s+Overig"),
                          ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Percentage: Overige", r"Overige"),
                          ("Note. Relevante risico’s ten aanzien van de financiële instrumenten / Portefeuillesamenstelling naar sector Percentage: Overig", r"Overig")
                          ]


overige_vorderingen_lineitems = [("Note. Overige vorderingen / specificatie overige vorderingen: Rekening-courant met Stichting TKP Pensioen Treasury", r"Rekening\-courant\s+met\s+Stichting\s+TKP\s+Pensioen\s+Treasury"),
                                 ("Note. Overige vorderingen / specificatie overige vorderingen: Inzake beheervergoeding", r"Inzake\s+beheervergoeding\s+\(base\s+fee\)"),
                                 ("Note. Overige vorderingen / specificatie overige vorderingen: Belastingen", r"Belastingen"),
                                 ("Note. Overige vorderingen / specificatie overige vorderingen: Dividenden", r"Dividenden"),
                                 ("Note. Overige vorderingen / specificatie overige vorderingen: Lopende rente obligaties", r"Lopende\s+rente\s+obligaties"),
                                 ("Note. Overige vorderingen / specificatie overige vorderingen: Securities lending", r"Securities\s+lending"),
                                 ("Note. Overige vorderingen / specificatie overige vorderingen: Marginrekeningen", r"Marginrekeningen"),
                                 ("Note. Overige vorderingen / specificatie overige vorderingen: Cash collateral", r"Cash\s+collateral"),
                                 ("Note. Overige vorderingen / specificatie overige vorderingen: Overige", r"Overige"),
                                 ("Note. Overige vorderingen / specificatie overige vorderingen: Kas onderpand", r"Kas\s+onderpand"),
                                 ("Note. Overige vorderingen / specificatie overige vorderingen: Totaal overige vorderingen", r"Totaal\s+overige\s+vorderingen")
                                ]

mutatieoverzicht_fondsvermogen_participanten_lineitems = [("Note. Fondsvermogen Participanten / Mutatieoverzicht fondsvermogen participanten: Stand begin boekjaar", r"Stand\s+begin\s+boekjaar"),
                                                          ("Note. Fondsvermogen Participanten / Mutatieoverzicht fondsvermogen participanten: Stortingen", r"Stortingen"),
                                                          ("Note. Fondsvermogen Participanten / Mutatieoverzicht fondsvermogen participanten: Onttrekkingen", r"Onttrekkingen"),
                                                          ("Note. Fondsvermogen Participanten / Mutatieoverzicht fondsvermogen participanten: Overdracht van rechten", r"Overdracht\s+van\s+rechten"),
                                                          ("Note. Fondsvermogen Participanten / Mutatieoverzicht fondsvermogen participanten: Resultaat", r"Resultaat"),
                                                          ("Note. Fondsvermogen Participanten / Mutatieoverzicht fondsvermogen participanten: Stand einde boekjaar", r"Stand\s+einde\s+boekjaar")
                                                          ]


verloopoverzicht_fondsvermogen_participaties_lineitems = [("Note. Fondsvermogen Participanten / Verloopoverzicht participaties: Aantal participaties per 1 januari", r"Aantal\s+participaties\s+per\s+\d\s+januari"),
                                                          ("Note. Fondsvermogen Participanten / Verloopoverzicht participaties: Stortingen", r"Stortingen"),
                                                          ("Note. Fondsvermogen Participanten / Verloopoverzicht participaties: Onttrekkingen", r"Onttrekkingen"),
                                                          ("Note. Fondsvermogen Participanten / Verloopoverzicht participaties: Aantal participaties per 31 december", r"Aantal\s+participaties\s+per\s+\d\d\s+december")
                                                          ]

meerjarenoverzicht_fondsvermogen_participanten_lineitems = [("Note. Fondsvermogen Participanten / Meerjarenoverzicht fondsvermogen participanten: Fondsvermogen (x € 1.000)", r"Fondsvermogen\s+\(\s*x\s*€\s*1\.000\s*\)"),
                                                            ("Note. Fondsvermogen Participanten / Meerjarenoverzicht fondsvermogen participanten: Aantal units", r"Aantal\s+units"),
                                                            ("Note. Fondsvermogen Participanten / Meerjarenoverzicht fondsvermogen participanten: Unitwaarde (in €)", r"Unitwaarde\s+\(\s*in\s*€\s*\)")
                                                            ]

overige_schulden_lineitems = [("Note. Overige schulden / Specificatie overige schulden: Inzake niet afgewikkelde transacties", r"Inzake\s+niet\s+afgewikkelde\s+transacties"),
                    ("Note. Overige schulden / Specificatie overige schulden: Cash collateral", r"Cash\s+collateral"),
                    ("Note. Overige schulden / Specificatie overige schulden: fiscale kosten", r"fiscale\s+kosten"),
                    ("Note. Overige schulden / Specificatie overige schulden: Te betalen beheervergoeding", r"Te\s+betalen\s+beheervergoeding"),
                    ("Note. Overige schulden / Specificatie overige schulden: Te betalen performance fee", r"Te\s+betalen\s+performance"),
                    ("Note. Overige schulden / Specificatie overige schulden: Te betalen bewaarvergoeding", r"Te\s+betalen\s+bewaarvergoeding"),
                    ("Note. Overige schulden / Specificatie overige schulden: Te betalen koerskosten", r"Te\s+betalen\s+koerskosten"),
                    ("Note. Overige schulden / Specificatie overige schulden: Te betalen accountantskosten", r"Te\s+betalen\s+accountantskosten"),
                    ("Note. Overige schulden / Specificatie overige schulden: Te betalen juridische kosten", r"Te\s+betalen\s+juridische\s+kosten"),
                    ("Note. Overige schulden / Specificatie overige schulden: Te betalen kosten toezichthouder", r"Te\s+betalen\s+kosten\s+toezichthouder"),
                    ("Note. Overige schulden / Specificatie overige schulden: Te betalen administratie- en bankkosten", r"Te\s+betalen\s+administratie\-\s+en\s+bankkosten"),
                    ("Note. Overige schulden / Specificatie overige schulden: Te betalen interest", r"Te\s+betalen\s+interest"),
                    ("Note. Overige schulden / Specificatie overige schulden: Te betalen belastingen", r"Te\s+betalen\s+belastingen"),
                    ("Note. Overige schulden / Specificatie overige schulden: Overige schulden uit hoofde van beleggingsactiviteiten", r"Overige\s+schulden\s+uit\s+hoofde\s+van\s+beleggingsactiviteiten"),
                    ("Note. Overige schulden / Specificatie overige schulden: Totaal overige schulden", r"Totaal\s+overige\s+schulden")
                    ]

waardeveranderingen_beleggingen_lineitems = [("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Gerealiseerde koers- en valutawinsten op aandelen en aandelenfondsen", r"Gerealiseerde\s+koers\-\s+en\s+valutawinsten\s+op\s+aandelen\s+en\s+aandelenfondsen"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Gerealiseerde koers- en valutaverliezen op aandelen en aandelenfondsen", r"Gerealiseerde\s+koers\-\s+en\s+valutaverliezen\s+op\s+aandelen\s+en\s+aandelenfondsen"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Ongerealiseerde koers- en valutawinsten op aandelen en aandelenfondsen", r"Ongerealiseerde\s+koers\-\s+en\s+valutawinsten\s+op\s+aandelen\s+en\s+aandelenfondsen"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Ongerealiseerde koers- en valutaverliezen op aandelen en aandelenfondsen", r"Ongerealiseerde\s+koers\-\s+en\s+valutaverliezen\s+op\s+aandelen\s+en\s+aandelenfondsen"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Gerealiseerde koers- en valutawinsten op obligaties en obligatiefondsen", r"Gerealiseerde\s+koers\-\s+en\s+valutawinsten\s+op\s+obligaties\s+en\s+obligatiefondsen"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Gerealiseerde koers- en valutaverliezen op obligaties en obligatiefondsen", r"Gerealiseerde\s+koers\-\s+en\s+valutaverliezen\s+op\s+obligaties\s+en\s+obligatiefondsen"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Ongerealiseerde koers- en valutawinsten op obligaties en obligatiefondsen", r"Ongerealiseerde\s+koers\-\s+en\s+valutawinsten\s+op\s+obligaties\s+en\s+obligatiefondsen"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Ongerealiseerde koers- en valutaverliezen op obligaties en obligatiefondsen", r"Ongerealiseerde\s+koers\-\s+en\s+valutaverliezen\s+op\s+obligaties\s+en\s+obligatiefondsen"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Gerealiseerde koers- en valutawinsten op onroerend goed (fondsen)", r"Gerealiseerde\s+koers\-\s+en\s+valutawinsten\s+op\s+onroerend\s+goed\s+\(?fondsen\)?"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Gerealiseerde koers- en valutaverliezen op onroerend goed (fondsen)", r"Gerealiseerde\s+koers\-\s+en\s+valutaverliezen\s+op\s+onroerend\s+goed\s+\(?fondsen\)?"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Ongerealiseerde koers- en valutawinsten op onroerend goed (fondsen)", r"Ongerealiseerde\s+koers\-\s+en\s+valutawinsten\s+op\s+onroerend\s+goed\s+\(?fondsen\)?"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Ongerealiseerde koers- en valutaverliezen op onroerend goed (fondsen)", r"Ongerealiseerde\s+koers\-\s+en\s+valutaverliezen\s+op\s+onroerend\s+goed\s+\(?fondsen\)?"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Gerealiseerde koers- en valutawinsten op aandelenfutures", r"Gerealiseerde\s+koers\-\s+en\s+valutawinsten\s+op\s+aandelenfutures"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Gerealiseerde koers- en valutaverliezen op aandelenfutures", r"Gerealiseerde\s+koers\-\s+en\s+valutaverliezen\s+op\s+aandelenfutures"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Ongerealiseerde koers- en valutawinsten op aandelenfutures", r"Ongerealiseerde\s+koers\-\s+en\s+valutawinsten\s+op\s+aandelenfutures"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Ongerealiseerde koers- en valutaverliezen op aandelenfutures", r"Ongerealiseerde\s+koers\-\s+en\s+valutaverliezen\s+op\s+aandelenfutures"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Gerealiseerde koers- en valutawinsten op obligatiefutures", r"Gerealiseerde\s+koers\-\s+en\s+valutawinsten\s+op\s+obligatiefutures"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Gerealiseerde koers- en valutaverliezen op obligatiefutures", r"Gerealiseerde\s+koers\-\s+en\s+valutaverliezen\s+op\s+obligatiefutures"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Ongerealiseerde koers- en valutawinsten op obligatiefutures", r"Ongerealiseerde\s+koers\-\s+en\s+valutawinsten\s+op\s+obligatiefutures"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Ongerealiseerde koers- en valutaverliezen op obligatiefutures", r"Ongerealiseerde\s+koers\-\s+en\s+valutaverliezen\s+op\s+obligatiefutures"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Gerealiseerde koers- en valutawinsten op commodityfutures", r"Gerealiseerde\s+koers\-\s+en\s+valutawinsten\s+op\s+commodityfutures"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Gerealiseerde koers- en valutaverliezen op commodityfutures", r"Gerealiseerde\s+koers\-\s+en\s+valutaverliezen\s+op\s+commodityfutures"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Ongerealiseerde koers- en valutawinsten op commodityfutures", r"Ongerealiseerde\s+koers\-\s+en\s+valutawinsten\s+op\s+commodityfutures"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Ongerealiseerde koers- en valutaverliezen op commodityfutures", r"Ongerealiseerde\s+koers\-\s+en\s+valutaverliezen\s+op\s+commodityfutures"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Gerealiseerde koers- en valutawinsten op valutafutures", r"Gerealiseerde\s+koers\-\s+en\s+valutawinsten\s+op\s+valutafutures"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Gerealiseerde koers- en valutaverliezen op valutafutures", r"Gerealiseerde\s+koers\-\s+en\s+valutaverliezen\s+op\s+valutafutures"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Ongerealiseerde koers- en valutawinsten op valutafutures", r"Ongerealiseerde\s+koers\-\s+en\s+valutawinsten\s+op\s+valutafutures"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Ongerealiseerde koers- en valutaverliezen op valutafutures", r"Ongerealiseerde\s+koers\-\s+en\s+valutaverliezen\s+op\s+valutafutures"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Gerealiseerde koers- en valutawinsten op valutatermijncontracten", r"Gerealiseerde\s+koers\-\s+en\s+valutawinsten\s+op\s+valutatermijncontracten"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Gerealiseerde koers- en valutaverliezen op valutatermijncontracten", r"Gerealiseerde\s+koers\-\s+en\s+valutaverliezen\s+op\s+valutatermijncontracten"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Ongerealiseerde koers- en valutawinsten op valutatermijncontracten", r"Ongerealiseerde\s+koers\-\s+en\s+valutawinsten\s+op\s+valutatermijncontracten"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Ongerealiseerde koers- en valutaverliezen op valutatermijncontracten", r"Ongerealiseerde\s+koers\-\s+en\s+valutaverliezen\s+op\s+valutatermijncontracten"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Gerealiseerde koers- en valutawinsten op commodity fondsen", r"Gerealiseerde\s+koers\-\s+en\s+valutawinsten\s+op\s+commodity\s+fondsen"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Gerealiseerde koers- en valutaverliezen op commodity fondsen", r"Gerealiseerde\s+koers\-\s+en\s+valutaverliezen\s+op\s+commodity\s+fondsen"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Ongerealiseerde koers- en valutawinsten op commodity fondsen", r"Ongerealiseerde\s+koers\-\s+en\s+valutawinsten\s+op\s+commodity\s+fondsen"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Ongerealiseerde koers- en valutaverliezen op commodity fondsen", r"Ongerealiseerde\s+koers\-\s+en\s+valutaverliezen\s+op\s+commodity\s+fondsen"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Gerealiseerde winsten onroerend goed (fondsen)", r"Gerealiseerde\s+winsten\s+onroerend\s+goed\s+\(?fondsen\)?"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Gerealiseerde verliezen onroerend goed (fondsen)", r"Gerealiseerde\s+verliezen\s+onroerend\s+goed\s+\(?fondsen\)?"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Ongerealiseerde winsten onroerend goed (fondsen)", r"Ongerealiseerde\s+winsten\s+onroerend\s+goed\s+\(?fondsen\)?"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Ongerealiseerde verliezen onroerend goed (fondsen)", r"Ongerealiseerde\s+verliezen\s+onroerend\s+goed\s+\(?fondsen\)?"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Gerealiseerde winsten geldmarktfondsen", r"Gerealiseerde\s+winsten\s+geldmarktfondsen"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Gerealiseerde verliezen geldmarktfondsen", r"Gerealiseerde\s+verliezen\s+geldmarktfondsen"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Ongerealiseerde winsten geldmarktfondsen", r"Ongerealiseerde\s+winsten\s+geldmarktfondsen"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Ongerealiseerde verliezen geldmarktfondsen", r"Ongerealiseerde\s+verliezen\s+geldmarktfondsen"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Gerealiseerde winsten valutatermijncontracten", r"Gerealiseerde\s+winsten\s+valutatermijncontracten"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Gerealiseerde verliezen valutatermijncontracten", r"Gerealiseerde\s+verliezen\s+valutatermijncontracten"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Ongerealiseerde winsten valutatermijncontracten", r"Ongerealiseerde\s+winsten\s+valutatermijncontracten"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Ongerealiseerde verliezen valutatermijncontracten", r"Ongerealiseerde\s+verliezen\s+valutatermijncontracten"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Gerealiseerd resultaat hypotheekfondsen", r"Gerealiseerd\s+resultaat\s+hypotheekfondsen"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Ongerealiseerd resultaat hypotheekfondsen", r"Ongerealiseerd\s+resultaat\s+hypotheekfondsen"),
                                             ("Note. Waardeveranderingen van beleggingen / Specificatie Waardeveranderingen van beleggingen: Totaal waardeveranderingen van beleggingen", r"Totaal\s+waardeveranderingen\s+van\s+beleggingen")
                                             ]


lopende_kosten_lineitems = [("Note. Kosten / Lopende kosten factor: Totale kosten binnen het fonds", r"Totale\s+kosten\s+binnen\s+het\s+fonds"),
                            ("Note. Kosten / Lopende kosten factor: Toegerekende kosten onderliggende beleggingsfondsen", r"Toegerekende\s+kosten\s+onderliggende\s+beleggingsfondsen"),
                            ("Note. Kosten / Lopende kosten factor: Toegerekende kosten onderliggende TKPI beleggingsfondsen", r"Toegerekende\s+kosten\s+onderliggende\s+TKPI\s+beleggingsfondsen"),
                            ("Note. Kosten / Lopende kosten factor: Toegerekende kosten onderliggende extern beheerde beleggingsfondsen", r"Toegerekende\s+kosten\s+onderliggende\s+extern\s+beheerde\s+beleggingsfondsen"),
                            ("Note. Kosten / Lopende kosten factor: Totaal fee sharing agreements (securities lending fees)", r"Totaal\s+fee\s+sharing\s+agreements\s+\(securities\s+lending\s+fees\)"),
                            ("Note. Kosten / Lopende kosten factor: Totale kosten", r"Totale\s+kosten"),
                            ("Note. Kosten / Lopende kosten factor: Gemiddelde intrinsieke waarde", r"Gemiddelde\s+intrinsieke\s+waarde"),
                            ("Note. Kosten / Lopende kosten factor: Lopende kosten factor (LKF)", r"Lopende\s+kosten\s+factor\s+\(\s*LKF\s*\)")
                            ]

prestatievergoeding_lineitems = [("Note. Kosten / prestatievergoeding: Totale prestatievergoeding binnen het fonds", r"Totale\s+prestatievergoeding\s+binnen\s+het\s+fonds"),
                                 ("Note. Kosten / prestatievergoeding: Toegerekende prestatievergoeding onderliggende beleggingsfondsen", r"Toegerekende\s+prestatievergoeding\s+onderliggende\s+beleggingsfondsen"),
                                 ("Note. Kosten / prestatievergoeding: Toegerekende prestatievergoeding onderliggende TKPI beleggingsfondsen", r"Toegerekende\s+prestatievergoeding\s+onderliggende\s+TKPI\s+beleggingsfondsen"),
                                 ("Note. Kosten / prestatievergoeding: Toegerekende prestatievergoeding onderliggende extern beheerde beleggingsfondsen", r"Toegerekende\s+prestatievergoeding\s+onderliggende\s+extern\s+beheerde\s+beleggingsfondsen"),
                                 ("Note. Kosten / prestatievergoeding: Totale prestatievergoeding", r"Totaa?le?\s+prestatievergoedinge?n?"),
                                 ("Note. Kosten / prestatievergoeding: Prestatievergoedingen (%)", r"\W\s+Prestatievergoeding(?:en|\s+\(\s*%\s*\))")
                                 ]

geidentificeerde_transactiekosten_lineitems = [("Note. Kosten / Geïdentificeerde transactiekosten: Totale transactiekosten binnen het fonds", r"Totale\s+transactiekosten\s+binnen\s+het\s+fonds"),
                                               ("Note. Kosten / Geïdentificeerde transactiekosten: Toegerekende transactiekosten onderliggende beleggingsfondsen", r"Toegerekende\s+transactiekosten\s+onderliggende\s+beleggingsfondsen"),
                                               ("Note. Kosten / Geïdentificeerde transactiekosten: Toegerekende transactiekosten onderliggende TKPI beleggingsfondsen", r"Toegerekende\s+transactiekosten\s+onderliggende\s+TKPI\s+beleggingsfondsen"),
                                               ("Note. Kosten / Geïdentificeerde transactiekosten: Toegerekende transactiekosten onderliggende extern beheerde beleggingsfondsen", r"Toegerekende\s+transactiekosten\s+onderliggende\s+extern\s+beheerde\s+beleggingsfondsen"),
                                               ("Note. Kosten / Geïdentificeerde transactiekosten: Totale transactiekosten (bruto)", r"Totale\s+transactiekosten\s+(?:\(bruto\))?"),
                                               ("Note. Kosten / Geïdentificeerde transactiekosten: Toe- en uittredingsvergoedingen", r"Toe\-\s+en\s+uittredingsvergoedingen"),
                                               ("Note. Kosten / Geïdentificeerde transactiekosten: Totale transactiekosten na toe- en uittredingsvergoedingen", r"Totale\s+transactiekosten\s+na\s+toe\-\s+en\s+uittredingsvergoedingen"),
                                               ("Note. Kosten / Geïdentificeerde transactiekosten: Transactiekosten (%)", r"\W\s+Transactiekosten\s*\(?\s?%?\s?\)?")
                                               ]

overige_toelichtingen_lineitems = [("Note. Overige toelichtingen / Omloopfactor: Effecten aankopen", r"Effecten\s+aankopen"),
                                   ("Note. Overige toelichtingen / Omloopfactor: Effecten verkopen", r"Effecten\s+verkopen"),
                                   ("Note. Overige toelichtingen / Omloopfactor: Totaal van beleggingstransacties", r"Totaal\s+van\s+beleggingstransacties"),
                                   ("Note. Overige toelichtingen / Omloopfactor: Uitgifte participaties", r"Uitgifte\s+participaties"),
                                   ("Note. Overige toelichtingen / Omloopfactor: Inkoop participaties", r"Inkoop\s+participaties"),
                                   ("Note. Overige toelichtingen / Omloopfactor: Totaal mutaties in participaties", r"Totaal mutaties\s+in\s+participaties"),
                                   ("Note. Overige toelichtingen / Omloopfactor: Gemiddelde intrinsieke waarde van het fonds", r"Gemiddelde\s+intrinsieke\s+waarde\s+van\s+het\s+fonds"),
                                   ("Note. Overige toelichtingen / Omloopfactor: Omloopfactor", r"Omloopfactor")
                                   ]

kerncijfers_fondsvermogen_lineitems = [("Kerncijfers / fondsvermogen : Fondsvermogen (x € 1.000)", r"Fondsvermogen\s+\(\s*x\s*€\s*1\.000\s*\)"),
                                       ("Kerncijfers / fondsvermogen : Aantal units", r"Aantal\s+units"),
                                       ("Kerncijfers / fondsvermogen : Unitwaarde (in €)", r"Unitwaarde\s+\(\s*in\s*€\s*\)")
                                       ]

kerncijfers_rendement_lineitems = [("Kerncijfers / Rendement : Netto rendement", r"Netto\s+rendement"),
                                   ("Kerncijfers / Rendement : Rendement benchmark", r"Rendement\s+benchmark"),
                                   ("Kerncijfers / Rendement : Outperformance", r"Outperformance"),
                                   ("Kerncijfers / Rendement : Outperformance sinds inceptie", r"Outperformance\s+sinds\s+inceptie"),
                                   ("Kerncijfers / Rendement : Annualized outperformance sinds inceptie", r"Annualized\s+outperformance\s+sinds\s+inceptie")
                                   ]


kerncijfers_waardeontwikkeling_lineitems = [("Kerncijfers / Waardeontwikkeling : Inkomsten", r"Inkomsten"),
                                            ("Kerncijfers / Waardeontwikkeling : Waardeveranderingen", r"Waardeveranderingen"),
                                            ("Kerncijfers / Waardeontwikkeling : Overig resultaat", r"Overig\s+resultaat"),
                                            ("Kerncijfers / Waardeontwikkeling : Kosten", r"Kosten")
                                            ]

kerncijfers_waardeontwikkeling_perunit_lineitems = [("Kerncijfers / Waardeontwikkeling per unit : Inkomsten", r"Inkomsten"),
                                                    ("Kerncijfers / Waardeontwikkeling per unit : Waardeveranderingen", r"Waardeveranderingen"),
                                                    ("Kerncijfers / Waardeontwikkeling per unit : Overig resultaat", r"Overig\s+resultaat"),
                                                    ("Kerncijfers / Waardeontwikkeling per unit : Kosten", r"Kosten")
                                                    ]


kerncijfers_ratio_lineitems = [("Kerncijfers / Ratio's : Lopende Kosten Factor (LKF)", r"Lopende\s+Kosten\s+Factor\s+\(LKF\)"),
                               ("Kerncijfers / Ratio's : Prestatievergoeding", r"Prestatievergoeding"),
                               ("Kerncijfers / Ratio's : Transactiekosten", r"Transactiekosten"),
                               ("Kerncijfers / Ratio's : Omloopfactor", r"Omloopfactor")
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
    text_concat_balance = find_tables(text_concat, r"(\d\s+Jaarrekening\s+\d\.\d\s+Balans\s+Balans(.*?)\d\.\d\s+Winst\-?\s+en\s+verliesrekening)")
    text_concat_balance_debit = find_tables(text_concat_balance, r"(Activa(.*?)Passiva)")
    text_concat_balance_credit = find_tables(text_concat_balance, r"(Passiva(.+))")
    text_concat_pl = find_tables(text_concat, r"(\d\.\d\s+Winst\-?\s+en\s+verliesrekening\s+Winst\-?\s+en\s+verliesrekening(.*?)\d\.\d\s+Kasstroomoverzicht)")
    text_concat_cashflow = find_tables(text_concat, r"(\d\.\d\s+Kasstroomoverzicht\s+Kasstroomoverzicht(.*?)\s+Toelichting op de balans)")
    text_concat_toelichting = find_tables(text_concat, r"(\d\.\d\s+Toelichting\s+op\s+de\s+balans\s+en\s+Winst\-?\s*en\s+verliesrekening\s*[^\.]{2}(.*?)\d\.\s+Relevante\s+risico[’']s\s+ten\s+aanzien\s+van\s+de\s+financiële\s+instrumenten)")
    text_concat_toelichting_aandelen = find_tables(text_concat_toelichting, r"(Mutatieoverzicht\s+aandelen\s+en\s+aandelenfondsen\s+\(bedragen(.*?)Marktwaarde\s+einde\s+boekjaar\s+[\d\.\-]+\s+[\d\.\-]+)")
    text_concat_toelichting_obligaties = find_tables(text_concat_toelichting, r"(Mutatieoverzicht\s+obligaties\s+en\s+obligatiefondsen\s+\(bedragen(.*?)Marktwaarde\s+einde\s+boekjaar\s+[\d\.\-]+\s+[\d\.\-]+)")
    text_concat_toelichting_onroerend = find_tables(text_concat_toelichting, r"(Mutatieoverzicht\s+onroerend\s+goed\s+\(fondsen\)\s+\(bedragen(.*?)Marktwaarde\s+einde\s+boekjaar\s+[\d\.\-]+\s+[\d\.\-]+)")
    text_concat_toelichting_aandelenfutures = find_tables(text_concat_toelichting, r"(Mutatieoverzicht\s+aandelenfutures\s+\(bedragen(.*?)Marktwaarde\s+einde\s+boekjaar\s+[\d\.\-]+\s+[\d\.\-]+)")
    text_concat_toelichting_valutatermijncontracten = find_tables(text_concat_toelichting, r"(Mutatieoverzicht\s+valutatermijncontracten\s+\(bedragen(.*?)Marktwaarde\s+einde\s+boekjaar\s+[\d\.\-]+\s+[\d\.\-]+)")
    text_concat_toelichting_vastgoed = find_tables(text_concat_toelichting, r"(Mutatieoverzicht\s+vastgoed\s+\(fondsen\)\s+\(bedragen(.*?)Marktwaarde\s+einde\s+boekjaar\s+[\d\.\-]+\s+[\d\.\-]+)")
    text_concat_toelichting_geldmarktfondsen = find_tables(text_concat_toelichting, r"(Mutatieoverzicht\s+geldmarktfondsen\s+\(bedragen(.*?)Marktwaarde\s+einde\s+boekjaar\s+[\d\.\-]+\s+[\d\.\-]+)")
    text_concat_toelichting_hypotheekfondsen = find_tables(text_concat_toelichting, r"(Mutatieoverzicht\s+hypotheekfondsen\s+\(bedragen(.*?)Marktwaarde\s+einde\s+boekjaar\s+[\d\.\-]+\s+[\d\.\-]+)")  
    text_concat_countries = find_tables(text_concat, r"(Portefeuillesamenstelling\s+naar\s+land\s+\(bedragen(.*?)Totaal\s+[\d\.]+\s+)")
    text_concat_industries = find_tables(text_concat, r"(Portefeuillesamenstelling\s+naar\s+sector\s+\(bedragen(.*?)Totaal\s+[\d\.]+\s+)")
    text_concat_overige_vorderingen = find_tables(text_concat, r"(Specificatie\s+overige\s+vorderingen\s+\(bedragen(.*?)Totaal\s+overige\s+vorderingen\s+[\d\.\-]+\s+[\d\.\-]+)")
    text_concat_mutatieoverzicht_fondsvermogen_participanten = find_tables(text_concat, r"(Mutatieoverzicht\s+fondsvermogen\s+participanten\s+\(bedragen(.*?)Stand\s+einde\s+boekjaar\s+[\d\.\-]+\s+[\d\.\-]+)")
    text_concat_verloopoverzicht_fondsvermogen_participaties = find_tables(text_concat, r"(Verloopoverzicht\s+fondsvermogen\s+participaties\s+\(bedragen(.*?)Aantal\s+participaties\s+per\s+\d\d\s+december\s+[\d\.\-]+\s+[\d\.\-]+)")
    text_concat_meerjarenoverzicht_fondsvermogen_participanten = find_tables(text_concat, r"(Meerjarenoverzicht\s+fondsvermogen\s+participanten\s+\d(.*?)Unitwaarde\s+\(\s*in\s*€\s*\)\s+[\d\,\-]+\s+[\d\,\-]+\s+[\d\,\-]+)")
    text_concat_overige_schulden = find_tables(text_concat, r"(Specificatie\s+overige\s+schulden\s+\(bedragen(.*?)Totaal\s+overige\s+schulden\s+[\d\.\-]+\s+[\d\.\-]+)")
    text_concat_waardeveranderingen_beleggingen = find_tables(text_concat, r"(Specificatie\s+waardeveranderingen\s+van\s+beleggingen\s+\(bedragen(.*?)Totaal\s+waardeveranderingen\s+van\s+beleggingen\s+[\d\.\-]+\s+[\d\.\-]+)")
    text_concat_lopende_kosten = find_tables(text_concat, r"(Lopende\s+kosten\s+factor\s+\(bedragen(.*?)Lopende\s+kosten\s+factor\s+\(\s*LKF\s*\)\s+[\d\,%\-]+\s+[\d\,%\-]+)")
    text_concat_prestatievergoeding = find_tables(text_concat, r"(prestatievergoeding\s+\(bedragen(.*?)Prestatievergoeding(en\s+|\s+\(%\)\s+)[\d\,\-%]+\s+[\d\,\-%]+%)")
    text_concat_geidentificeerde_transactiekosten = find_tables(text_concat, r"(Geïdentificeerde\s+transactiekosten\s+\(bedragen(.*?)Transactiekosten\s*\(?\s?%?\s?\)?\s*[\d\,\-%]+\s+[\d\,\-%]+%)")
    text_concat_overige_toelichtingen = find_tables(text_concat, r"(Omloopfactor\s+\(bedragen(.*?)Omloopfactor\s+[\d\.\-]+\s+[\d\.\-]+)")
    text_concat_kerncijfers = find_tables(text_concat, r"(\d\s+Kerncijfers\s+[^\.]{3}(.*?)\d\s+Verslag\s+van\s+de\s+beheerder)")
    text_concat_kerncijfers_fondsvermogen = find_tables(text_concat_kerncijfers, r"(Fondsvermogen(.*?)Rendement)")
    text_concat_kerncijfers_rendement = find_tables(text_concat_kerncijfers, r"(Rendement(.*?)waardeontwikkeling)")
    text_concat_kerncijfers_waardeontwikkeling = find_tables(text_concat_kerncijfers, r"(Waardeontwikkeling\s+\(bedragen(.*?)Totaal\s+resultaat\s+[\d\.\,\-]+\s+[\d\.\,\-]+)")
    text_concat_kerncijfers_waardeontwikkeling_perunit = find_tables(text_concat_kerncijfers, r"(waardeontwikkeling\s+per\s+unit(.*?)Totaal\s+resultaat\s+[\d\.\,\-]+\s+[\d\.\,\-]+)")
    text_concat_kerncijfers_ratio = find_tables(text_concat_kerncijfers, r"(Ratio[’']s(.*?)Omloopfactor\s+[\d\.\,\-]+\s+[\d\.\,\-]+)")

    # Create empty dictionaries for each table
    # These dictionaries will contain the extracted lineitems with the extracted numbers
    balance_sheet_debit = {}
    balance_sheet_credit = {}
    pl_account = {}
    cashflow_statement = {}
    toelichting_aandelen_table = {}
    toelichting_obligaties_table = {}
    toelichting_onroerend_table = {}
    toelichting_aandelenfutures_table = {}
    toelichting_valutatermijncontracten_table = {}
    toelichting_vastgoed_table = {}
    toelichting_geldmarktfondsen_table = {}
    toelichting_hypotheekfondsen_table = {}
    portfolio_countries_amount = {}
    portfolio_countries_percentage = {}
    portfolio_industries_amount = {}
    portfolio_industries_percentage = {}
    overige_vorderingen_table = {}
    mutatieoverzicht_fondsvermogen_participanten_table = {}
    verloopoverzicht_fondsvermogen_participaties_table = {}
    meerjarenoverzicht_fondsvermogen_participanten_table = {}
    overige_schulden_table = {}
    waardeveranderingen_beleggingen_table = {}
    lopende_kosten_table = {}
    prestatievergoeding_table = {}
    geidentificeerde_transactiekosten_table = {}
    overige_toelichtingen_table = {}
    kerncijfers_fondsvermogen_table = {}
    kerncijfers_rendement_table = {}
    kerncijfers_waardeontwikkeling_table = {}
    kerncijfers_waardeontwikkeling_perunit_table = {}
    kerncijfers_ratio_table = {}
    
    
    # The list below contains tuples with objects for each table
    # The first element is the empty dictionary that will contain the lineitems and extracted numbers
    # The second element is table that contains the lineitem tuples
    # The third element is the extracted table in string format
    # The fouth element is the regex pattern that is used to extract the numbers from the tables
    # The final element specifies the position of the amount that needs to be extracted. Most often this will be a 0 for the first amount. Sometimes it will be 1 for the second amount.
    items = [(balance_sheet_debit, balance_debit_lineitems, text_concat_balance_debit, pattern_integers, 0),
             (balance_sheet_credit, balance_credit_lineitems, text_concat_balance_credit, pattern_integers, 0),
             (pl_account, profitloss_lineitems, text_concat_pl, pattern_integers, 0),
             (cashflow_statement, cashflow_lineitems, text_concat_cashflow, pattern_integers, 0),
             (toelichting_aandelen_table, toelichting_aandelen_lineitems, text_concat_toelichting_aandelen, pattern_integers, 0),
             (toelichting_obligaties_table, toelichting_obligaties_lineitems, text_concat_toelichting_obligaties, pattern_integers, 0),
             (toelichting_onroerend_table, toelichting_onroerend_lineitems, text_concat_toelichting_onroerend, pattern_integers, 0),
             (toelichting_aandelenfutures_table, toelichting_aandelenfutures_lineitems, text_concat_toelichting_aandelenfutures, pattern_integers, 0),
             (toelichting_valutatermijncontracten_table, toelichting_valutatermijncontracten_lineitems, text_concat_toelichting_valutatermijncontracten, pattern_integers, 0),
             (toelichting_vastgoed_table, toelichting_vastgoed_lineitems, text_concat_toelichting_vastgoed, pattern_integers, 0),
             (toelichting_geldmarktfondsen_table, toelichting_geldmarktfondsen_lineitems, text_concat_toelichting_geldmarktfondsen, pattern_integers, 0),
             (toelichting_hypotheekfondsen_table, toelichting_hypotheekfondsen_lineitems, text_concat_toelichting_hypotheekfondsen, pattern_integers, 0),
             (portfolio_countries_amount, countries_amounts, text_concat_countries, pattern_portfolio, 0),
             (portfolio_countries_percentage, countries_percentages, text_concat_countries, pattern_portfolio, 1),
             (portfolio_industries_amount, industries_amounts, text_concat_industries, pattern_portfolio, 0),
             (portfolio_industries_percentage, industries_percentages, text_concat_industries, pattern_portfolio, 1),
             (overige_vorderingen_table, overige_vorderingen_lineitems, text_concat_overige_vorderingen, pattern_integers, 0),
             (mutatieoverzicht_fondsvermogen_participanten_table, mutatieoverzicht_fondsvermogen_participanten_lineitems, text_concat_mutatieoverzicht_fondsvermogen_participanten, pattern_integers, 0),
             (verloopoverzicht_fondsvermogen_participaties_table, verloopoverzicht_fondsvermogen_participaties_lineitems, text_concat_verloopoverzicht_fondsvermogen_participaties, pattern_integers, 0),
             (meerjarenoverzicht_fondsvermogen_participanten_table, meerjarenoverzicht_fondsvermogen_participanten_lineitems, text_concat_meerjarenoverzicht_fondsvermogen_participanten, pattern_integerfloat, 0),
             (overige_schulden_table, overige_schulden_lineitems, text_concat_overige_schulden, pattern_integers, 0),
             (waardeveranderingen_beleggingen_table, waardeveranderingen_beleggingen_lineitems, text_concat_waardeveranderingen_beleggingen, pattern_integers, 0),
             (lopende_kosten_table, lopende_kosten_lineitems, text_concat_lopende_kosten, pattern_integerfloat, 0),
             (prestatievergoeding_table, prestatievergoeding_lineitems, text_concat_prestatievergoeding, pattern_integerfloat, 0),
             (geidentificeerde_transactiekosten_table, geidentificeerde_transactiekosten_lineitems, text_concat_geidentificeerde_transactiekosten, pattern_integerfloat, 0),
             (overige_toelichtingen_table, overige_toelichtingen_lineitems, text_concat_overige_toelichtingen, pattern_integers, 0),
             (kerncijfers_fondsvermogen_table, kerncijfers_fondsvermogen_lineitems, text_concat_kerncijfers_fondsvermogen, pattern_integerfloat, 0),
             (kerncijfers_rendement_table, kerncijfers_rendement_lineitems, text_concat_kerncijfers_rendement, pattern_integerfloat, 0),
             (kerncijfers_waardeontwikkeling_table, kerncijfers_waardeontwikkeling_lineitems, text_concat_kerncijfers_waardeontwikkeling, pattern_integerfloat, 0),
             (kerncijfers_waardeontwikkeling_perunit_table, kerncijfers_waardeontwikkeling_perunit_lineitems, text_concat_kerncijfers_waardeontwikkeling_perunit, pattern_integerfloat, 0),
             (kerncijfers_ratio_table, kerncijfers_ratio_lineitems, text_concat_kerncijfers_ratio, pattern_integerfloat, 0)
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

# write to csv output file
with open(outputcsvfile, "w", newline="") as f:
    writer = csv.writer(f, delimiter=";")
    for row in funds_items:
        writer.writerow(row)





