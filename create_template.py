import json
from pathlib import Path
from commands.path_config import PATH

# Repeat term data due to kernel reset
terms = [
    ("confidentiality", r"\b(confidential(ity)?|non-disclosure|keep\s+secret|shall\s+not\s+disclose)\b", "Confidentiality clauses restricting disclosure of information."),
    ("non_disclosure", r"\b(non-disclosure|NDA|shall\s+not\s+disclose)\b", "Explicit non-disclosure agreement terms."),
    ("scope_of_services", r"\b(scope\s+of\s+services|services\s+to\s+be\s+provided|engagement\s+includes)\b", "Defines what services are included."),
    ("deliverables", r"\b(deliverables|work\s+product|outputs\s+to\s+be\s+delivered)\b", "Specifies required outcomes or documents."),
    ("use_of_information", r"\b(use\s+of\s+information|permitted\s+use|authorized\s+use)\b", "Permitted use of shared data or knowledge."),
    ("license_grant", r"\b(grant\s+of\s+license|license\s+to\s+use|licensed\s+rights)\b", "Specifies what license is granted."),
    ("intellectual_property", r"\b(intellectual\s+property|IP\s+rights|ownership|retain\s+rights)\b", "Ownership and usage of intellectual property."),
    ("work_product", r"\b(work\s+product|developed\s+materials|created\s+deliverables)\b", "Defines who owns the output."),
    ("data_protection", r"\b(data\s+protection|secure\s+storage|GDPR|privacy\s+policy)\b", "Obligations to protect data."),
    ("privacy_compliance", r"\b(privacy\s+compliance|HIPAA|CCPA|data\s+privacy\s+law)\b", "Mentions of compliance with privacy regulations."),
    ("payment_terms", r"\b(payment\s+terms|due\s+within|net\s+\d+|invoice|compensation)\b", "Details on how and when payments are made."),
    ("compensation", r"\b(compensation|salary|fee\s+structure|remuneration)\b", "Compensation amounts and structure."),
    ("fees", r"\b(fees|charges|billing\s+rates|service\s+fees)\b", "Fee schedule and amounts."),
    ("invoicing", r"\b(invoice|billing|payment\s+requests|submit\s+invoices)\b", "Invoicing procedures."),
    ("taxes", r"\b(taxes|tax\s+liability|withholding|VAT)\b", "Tax responsibilities and terms."),
    ("late_fees", r"\b(late\s+fee|penalty\s+for\s+late\s+payment|interest\s+on\s+overdue)\b", "Fees for missed payment deadlines."),
    ("cost_reimbursement", r"\b(cost\s+reimbursement|expenses\s+incurred|reimbursable\s+costs)\b", "Reimbursement of costs clause."),
    ("refund_policy", r"\b(refund\s+policy|return\s+of\s+funds|refund\s+upon\s+termination)\b", "Conditions under which funds are returned."),
    ("expenses", r"\b(expenses|out-of-pocket|travel\s+costs|approved\s+expenses)\b", "Expense coverage responsibilities."),
    ("royalties", r"\b(royalties|royalty\s+payments|licensing\s+fees)\b", "Payment terms tied to usage/licensing."),
    ("term", r"\b(term|duration|effective\s+date|valid\s+until|commencement\s+date)\b.*?(until|expires|termination|period)", "Start and end duration of the agreement."),
    ("termination", r"\b(termination|terminate|may\s+be\s+terminated|cancel\s+the\s+agreement)\b", "Termination rights and timelines."),
    ("renewal", r"\b(renewal|renew\s+automatically|extend\s+agreement)\b", "Renewal terms and notices."),
    ("auto_renewal", r"\b(auto\s+renew(al)?|renews\s+unless|automatically\s+renews)\b", "Automatically renewing terms."),
    ("notice_period", r"\b(notice\s+period|prior\s+notice|required|x\s+days\s+notice)\b", "Required notice time before change/termination."),
    ("cancellation_clause", r"\b(cancellation\s+clause|cancel\s+contract|terminate\s+without\s+cause)\b", "Right to cancel without fault."),
    ("governing_law", r"\b(governing\s+law|under\s+the\s+laws\s+of)\s+(the\s+State|jurisdiction)\b", "Which law governs the contract."),
    ("jurisdiction", r"\b(jurisdiction|venue|exclusive\s+jurisdiction|court\s+location)\b", "Where legal matters will be settled."),
    ("dispute_resolution", r"\b(dispute\s+resolution|arbitration|mediate|resolve\s+disputes)\b", "Methods of resolving disagreements."),
    ("arbitration", r"\b(arbitration|arbitrator|binding\s+decision|AAA)\b", "Arbitration terms and methods."),
    ("injunctive_relief", r"\b(injunctive\s+relief|equitable\s+relief|irreparable\s+harm)\b", "Right to prevent harm via court order."),
    ("force_majeure", r"\b(force\s+majeure|acts\s+of\s+god|unforeseen\s+events)\b", "Unexpected events that excuse obligation."),
    ("compliance_with_law", r"\b(comply\s+with\s+laws|legal\s+compliance|applicable\s+law)\b", "Obligation to follow applicable laws."),
    ("anti_corruption", r"\b(anti[-\s]?corruption|FCPA|bribery\s+laws)\b", "Adherence to anti-corruption laws."),
    ("regulatory_compliance", r"\b(regulatory\s+compliance|subject\s+to\s+regulations)\b", "Complying with specific regulations."),
    ("export_control", r"\b(export\s+control|ITAR|restricted\s+technology)\b", "Clauses around global technology transfer."),
    ("indemnity", r"\b(indemnif(y|ication)|hold\s+harmless|liability\s+for\s+damages)\b", "Protection from damages caused by the other party."),
    ("limitation_of_liability", r"\b(limit(ed)?\s+liability|cap\s+on\s+damages|max(imum)?\s+liability)\b", "Financial caps on responsibility."),
    ("warranty", r"\b(warranty|warranties|represent(ation)?|guarantee)\b", "Product or service guarantees."),
    ("disclaimer_of_warranty", r"\b(as\s+is|no\s+warranty|disclaims\s+all\s+warranties)\b", "Limitations on guarantees."),
    ("insurance", r"\b(insurance|coverage\s+limits|insured\s+party)\b", "Required insurance for risk management."),
    ("risk_of_loss", r"\b(risk\s+of\s+loss|damage\s+to\s+goods|responsibility\s+for\s+loss)\b", "Who bears risk of damage."),
    ("security", r"\b(security\s+measures|cybersecurity|secure\s+access|controls)\b", "Security protocols and controls."),
    ("assignment", r"\b(assign(ment)?|transfer\s+rights|delegate\s+obligations)\b", "Can the contract be transferred?"),
    ("subcontracting", r"\b(subcontracting|outsourcing|third\s+party\s+providers)\b", "Work passed to another vendor."),
    ("non_solicitation", r"\b(non-solicit|solicit\s+employees|recruit\s+restriction)\b", "Restricting party from poaching staff."),
    ("non_compete", r"\b(non-competition|non-compete|restrict\s+employment|competitive\s+activities)\b", "Post-termination competition rules."),
    ("exclusivity", r"\b(exclusivity|sole\s+provider|exclusive\s+right)\b", "One party gets exclusive rights."),
    ("independent_contractor", r"\b(independent\s+contractor|not\s+an\s+employee|self-employed)\b", "Defines relationship, avoids employment status."),
    ("entire_agreement", r"\b(entire\s+agreement|whole\s+agreement|supersedes\s+prior)\b", "No other promises outside the contract.")
]

# Save to JSON
output_path = PATH["templates"] / "full_terms.json"
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(json.dumps([
    {"key": key, "pattern": regex, "description": desc}
    for key, regex, desc in terms
], indent=2), encoding="utf-8")

str(output_path)
