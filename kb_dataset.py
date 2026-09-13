# kb_dataset.py
# Banking & FinTech Knowledge Base

"""
Reference knowledge base for the Banking & FinTech support agent.
"""
KB_DOCUMENTS = [

    {
        "doc_id": "KB001",
        "topic": "loan_eligibility",
        "title": "Loan Eligibility Criteria by Loan Type",
        "content": (
            "Loan eligibility depends on factors such as applicant age, income, "
            "employment or business stability, credit history, requested loan amount, "
            "and repayment capacity. Personal loans are generally unsecured, while "
            "home and auto loans are commonly linked to the financed property or vehicle. "
            "Education loans may involve a parent or guardian as co-applicant, while "
            "business loans may require evidence of business income and operating history."
        ),
        "source": "General banking lending practices"
    },

    {
        "doc_id": "KB002",
        "topic": "emi_calculation",
        "title": "EMI Calculation Rules",
        "content": (
            "An Equated Monthly Instalment is determined mainly by the loan principal, "
            "interest rate and repayment tenure. A longer tenure normally reduces the "
            "monthly instalment but can increase the total interest paid over the loan period. "
            "For floating-rate personal loans, changes in the benchmark interest rate can "
            "result in changes to the EMI, tenure, or both, and the borrower should be informed "
            "about the impact of such changes."
        ),
        "source": "Reserve Bank of India - Floating Rate EMI Directions"
    },

    {
        "doc_id": "KB003",
        "topic": "credit_card_fees",
        "title": "Credit Card Fee Structure",
        "content": (
            "Credit card charges can include joining or annual membership fees, "
            "late-payment charges, finance charges, cash-withdrawal fees and other "
            "transaction-related charges. The exact charges vary according to the card "
            "product and must be disclosed to the cardholder. Some cards may provide "
            "annual-fee waivers when specified spending conditions are met."
        ),
        "source": "HDFC Bank Credit Card Most Important Terms and Conditions"
    },

    {
        "doc_id": "KB004",
        "topic": "kyc_requirements",
        "title": "KYC Document Requirements",
        "content": (
            "Regulated financial institutions must perform customer due diligence before "
            "providing covered financial services. Customers may be required to provide "
            "identity information, address information, PAN or other officially valid "
            "documents depending on the product and applicable KYC rules. Financial "
            "institutions may also periodically update customer KYC information."
        ),
        "source": "Reserve Bank of India - KYC Directions"
    },

    {
        "doc_id": "KB005",
        "topic": "fraud_dispute",
        "title": "Fraud and Dispute Resolution Process",
        "content": (
            "Customers should report unauthorized electronic transactions to their bank "
            "as quickly as possible through the available complaint channels. Customer "
            "liability can depend on the cause of the transaction and the time taken to "
            "report it. Banks must provide a grievance process and take steps to prevent "
            "further unauthorized transactions after receiving the report."
        ),
        "source": "Reserve Bank of India - Customer Protection Directions"
    },

    {
        "doc_id": "KB006",
        "topic": "account_closure",
        "title": "Account Closure Process",
        "content": (
            "An account holder may request closure of an eligible bank account after "
            "completing the institution's verification and closure procedure. Outstanding "
            "dues, pending transactions, linked facilities or unresolved obligations may "
            "need to be settled before closure can be completed. After processing, the "
            "institution should update the account status and provide closure confirmation."
        ),
        "source": "General regulated banking account practices"
    },

    {
        "doc_id": "KB007",
        "topic": "interest_rate",
        "title": "Interest Rate Slabs",
        "content": (
            "Loan interest rates may be fixed or floating depending on the lending product. "
            "The offered rate can vary based on the type of loan, borrower credit profile, "
            "loan amount, tenure, collateral and lender risk assessment. A stronger credit "
            "profile and lower lending risk may result in more favourable pricing, subject "
            "to the lender's approved policy."
        ),
        "source": "Reserve Bank of India lending directions and general lender practices"
    },

    {
        "doc_id": "KB008",
        "topic": "prepayment",
        "title": "Prepayment and Foreclosure Rules",
        "content": (
            "Borrowers may be permitted to repay part or all of a loan before its scheduled "
            "maturity according to the loan agreement. Whether a prepayment or foreclosure "
            "charge applies depends on the type of loan, interest-rate structure and lender "
            "policy. Any applicable prepayment conditions should be disclosed to the borrower "
            "as part of the loan terms."
        ),
        "source": "RBI fair lending principles and lender loan terms"
    },

    {
        "doc_id": "KB009",
        "topic": "minimum_balance",
        "title": "Minimum Balance Requirements",
        "content": (
            "Minimum-balance requirements depend on the account product and financial "
            "institution. Some savings accounts may have no monthly average balance "
            "requirement, while other account variants may prescribe specific balance "
            "conditions. Customers should check the applicable account schedule before "
            "opening or operating the account."
        ),
        "source": "SBI Savings Account product information"
    },

    {
        "doc_id": "KB010",
        "topic": "credit_score",
        "title": "Credit Score Impact Factors",
        "content": (
            "A borrower's credit profile can be affected by repayment behaviour, outstanding "
            "credit, use of available credit, recent credit applications and overall credit "
            "history. Late payments, defaults and excessive borrowing can negatively affect "
            "creditworthiness. Regular repayment and responsible use of credit generally "
            "support a stronger credit profile."
        ),
        "source": "Credit-bureau and lending-industry credit assessment principles"
    },

    {
        "doc_id": "KB011",
        "topic": "joint_account",
        "title": "Joint Account Rules",
        "content": (
            "Bank accounts may be opened jointly by eligible account holders subject to "
            "the bank's KYC requirements. The holders can select an operating mandate such "
            "as jointly, either-or-survivor, former-or-survivor, or another permitted mode. "
            "The selected mandate determines which account holders are authorized to operate "
            "the account."
        ),
        "source": "SBI Savings Account eligibility information"
    },

    {
        "doc_id": "KB012",
        "topic": "nri_account",
        "title": "NRI Account Eligibility",
        "content": (
            "Eligible Non-Resident Indians may maintain designated NRI accounts such as "
            "NRE and NRO accounts, subject to applicable regulations and KYC requirements. "
            "An NRO account may be used for eligible Indian-source receipts, while NRE "
            "accounts are generally intended for qualifying overseas remittances. "
            "Applicants must provide the required identity, residency and KYC documents."
        ),
        "source": "State Bank of India NRI Account FAQs"
    },

    {
        "doc_id": "KB013",
        "topic": "loan_repayment",
        "title": "Loan Repayment and Missed EMI Policy",
        "content": (
            "Borrowers are expected to make scheduled EMI payments according to the agreed "
            "repayment schedule. A missed instalment can increase the pending amount and may "
            "lead to reminders, penal charges or further recovery action according to the "
            "loan agreement. Repeated missed repayments can also affect the borrower's "
            "credit profile and account classification."
        ),
        "source": "General banking repayment and fair-lending practices"
    },

    {
        "doc_id": "KB014",
        "topic": "loan_default_npa",
        "title": "Loan Default and NPA Classification",
        "content": (
            "A loan may move into default-related monitoring when scheduled repayments remain "
            "unpaid according to the loan terms. Under RBI prudential norms, a term loan is "
            "generally treated as a non-performing asset when interest or principal remains "
            "overdue for more than 90 days. NPA classification is therefore different from "
            "a single missed instalment and follows regulatory recognition rules."
        ),
        "source": "Reserve Bank of India - Prudential Norms on Income Recognition and NPA"
    },

    {
        "doc_id": "KB015",
        "topic": "loan_recovery",
        "title": "Loan Recovery Process",
        "content": (
            "When a borrower fails to make repayments, the lender may initiate recovery "
            "actions according to the loan agreement and applicable regulation. Recovery "
            "may involve reminders, repayment arrangements, notices or other permitted "
            "collection procedures. Recovery personnel must follow fair practices and "
            "should not use harassment, coercion or inappropriate collection behaviour."
        ),
        "source": "RBI Fair Practices principles"
    },

    {
        "doc_id": "KB016",
        "topic": "collateral",
        "title": "Collateral Requirements",
        "content": (
            "Secured loans may require an asset to be provided as collateral against the "
            "borrowed amount. Examples can include residential property, vehicles or eligible "
            "business assets depending on the loan product. The lender may assess the value "
            "and legal acceptability of the collateral before sanctioning the loan."
        ),
        "source": "General secured-lending practices"
    },

    {
        "doc_id": "KB017",
        "topic": "guarantor",
        "title": "Guarantor Requirements",
        "content": (
            "A lender may require a guarantor when additional repayment assurance is needed. "
            "The guarantor agrees to fulfil specified repayment obligations if the borrower "
            "fails to meet them, subject to the guarantee agreement. The lender may evaluate "
            "the guarantor's identity, financial capacity and credit profile before accepting "
            "the guarantee."
        ),
        "source": "General lending and guarantee practices"
    },

    {
        "doc_id": "KB018",
        "topic": "bank_lending",
        "title": "Bank Lending Policy",
        "content": (
            "Banks assess loan applications using factors such as borrower repayment capacity, "
            "credit history, income, loan purpose, tenure and applicable security. Approval "
            "does not depend on only one factor and remains subject to the bank's credit policy "
            "and regulatory requirements. The borrower should receive key loan terms including "
            "interest, repayment schedule and applicable charges."
        ),
        "source": "RBI fair lending framework and general banking practices"
    },

    {
        "doc_id": "KB019",
        "topic": "nbfc_lending",
        "title": "NBFC Lending Policy",
        "content": (
            "Non-Banking Financial Companies provide lending and other permitted financial "
            "services while operating under applicable RBI regulation. NBFCs may use their "
            "own approved underwriting models to assess income, repayment capacity, credit "
            "history and risk. Borrowers must be informed about important loan terms, charges "
            "and repayment obligations."
        ),
        "source": "Reserve Bank of India - NBFC regulatory framework"
    },

    {
        "doc_id": "KB020",
        "topic": "p2p_lending",
        "title": "Peer-to-Peer Lending Policy",
        "content": (
            "An RBI-registered NBFC-P2P platform acts as an intermediary connecting borrowers "
            "and lenders rather than lending its own funds. The platform cannot guarantee "
            "repayment or assure returns, and the lender bears the credit risk associated "
            "with the borrower. P2P lending on such platforms is unsecured, and prescribed "
            "fund transfers are carried out through escrow arrangements."
        ),
        "source": "Reserve Bank of India - NBFC-P2P Directions"
    }

]

MANDATORY_TOPICS = {
    "loan_eligibility",
    "emi_calculation",
    "credit_card_fees",
    "kyc_requirements",
    "fraud_dispute",
    "account_closure",
    "interest_rate",
    "prepayment",
    "minimum_balance",
    "credit_score",
    "joint_account",
    "nri_account"
}

def get_all_documents():
    return KB_DOCUMENTS


def get_document_by_id(doc_id):
    for document in KB_DOCUMENTS:
        if document["doc_id"] == doc_id:
            return document

    return None


def get_documents_by_topic(topic):
    return [
        document
        for document in KB_DOCUMENTS
        if document["topic"] == topic
    ]

def validate_knowledge_base():

    print("=" * 70)
    print("KNOWLEDGE BASE VALIDATION")
    print("=" * 70)

    assert len(KB_DOCUMENTS) >= 12

    available_topics = {
        document["topic"]
        for document in KB_DOCUMENTS
    }

    missing_topics = MANDATORY_TOPICS - available_topics

    assert not missing_topics, (
        f"Missing mandatory topics: {missing_topics}"
    )

    document_ids = [
        document["doc_id"]
        for document in KB_DOCUMENTS
    ]

    assert len(document_ids) == len(set(document_ids)), (
        "Duplicate document IDs detected."
    )

    for document in KB_DOCUMENTS:

        assert document["content"].strip(), (
            f'Empty content in {document["doc_id"]}'
        )

        print(
            f'{document["doc_id"]} | '
            f'{document["topic"]:<22} | '
            f'{document["title"]}'
        )

    print("-" * 70)
    print(f"Total documents       : {len(KB_DOCUMENTS)}")
    print("Mandatory topics      : Covered")
    print("Knowledge base status : VALID")
    print("=" * 70)


if __name__ == "__main__":
    validate_knowledge_base()
