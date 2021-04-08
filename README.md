# Audit Reconciliations

### Table of Contents
1. Summary
2. Motivation
3. File description
4. Licensing, Authors, Acknowledgements

## Summary <a name="summary"></a>
We present an algorithm to extract data from annual reports (PDF files) using the Python programming language with the aim to automate the financial statements during the auditing process.

## Motivation <a name="motivation"></a>
Auditors need to reconcile audit evidence to the object that they are auditing, which is often in a Portable Document Format (PDF). These reconciliations are a recurring task at every new version of the audit object. The reconciliations can be time-consuming, are generally not considered the most enjoyable task in the audit, are subject to human error and are of little added value to the auditee and financial statement users. Audit firms tend to offshore simple and standardizable audit tasks to shared service centers (Daugherty, Dickins, & Fennema, 2012). Outsourcing however comes at the expense of coordination costs, delays in the process (Hanes, 2013) and challenges regarding the liability risk that the auditor faces (Lyubimov, Arnold, & Sutton, 2013). This work presents an open-source algorithm to extract data from annual reports (PDF files) using a Python programming script to automate the financial statements reconciliations in an audit of Dutch investment funds. We jointly developed this use case as academics and practitioners and it resulted in a significant time saving for the audit team. The same technique can be applied to other countries and industries and has potential for academics to automate their data gather activities from filed financial statements in PDF format.

## Files description <a name="description"></a>
**audit_reconcilitions.py** is a Python file that can be run on the fly by just changing the path to the location of the relevant PDF files and by changing the output filename. Comments on each section of the code explain the performed steps. This is a relatively straightforward and simple to understand code, specifically designed for automating some of the basic auditing steps.

**Manual_script.pdf** is an outline of the procedure of how one can adapt the Python algorithm (audit_reconciliations.py) to one's needs and wishes. Some programming skills (preferably Python) and some experience with regular expressions is necessary.

**Sample-annual report-fund.pdf** is an artificially created sample PDF document that represents a typical annual report. One can use this file to test the algorithm.

**Robotic Process Automation for the Extraction.pdf** is the paper based on the work that is done, which is submitted to the journal "Current Issues in Auditing" of the American Accounting Association.

## Licensing, Authors, Acknowledgements <a name="licensing"></a>
This work is performed by: Alaa Khzam, Wim Janssen, Tjibbe Bosman, Jeroen Bellinga, and Seyit Hocuk. Most of the coding is done by Wim Janssen and Alaa Khzam.

We thank, Olof Bik, Arjan Brouwer, and Joris Roosen for their support, comments, and encouragement of this project.

Feel free to use the code.
