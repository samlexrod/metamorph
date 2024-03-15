insurance_claims_keywords = ['surgery', 'MRI', 'accident', 'arm', 'shoulder', 'injury', 'hospital', 'rehabilitation', 'physiotherapy', 'claim', 'compensation', 'liability', 'damages', 'policy', 'coverage', 'premium', 'deductible', 'adjuster', 'settlement', 'disability', 'fracture', 'trauma', 'emergency', 'x-ray', 'orthopedic', 'pain', 'treatment', 'medication', 'therapy', 'doctor', 'nurse', 'patient', 'healthcare', 'insurance', 'casualty']

# List of words related to an adjuster's note
adjuster_note_keywords = ['claim', 'policyholder', 'damage', 'estimate', 'coverage', 'liability', 'investigation', 'inspection', 'settlement', 'compensation', 'deductible', 'premium', 'loss', 'accident', 'injury', 'repair', 'replacement', 'documentation', 'evidence', 'adjustment', 'negotiation', 'dispute', 'resolution', 'claimant', 'insured', 'uninsured', 'underwriting', 'risk', 'fraud', 'denial', 'payment', 'recovery', 'subrogation', 'third-party', 'liability']

verbs = [
    'adjust', 'assess', 'claim', 'document', 'evaluate', 'inspect', 'investigate', 'negotiate', 'note', 'record', 'report', 'review', 'settle', 'verify', 'write', 'authorize', 'calculate', 'communicate', 'compare', 'confirm', 'consider', 'consult', 'determine', 'discuss', 'estimate', 'identify', 'inform', 'interpret', 'interview', 'manage', 'measure', 'observe', 'prepare', 'process', 'recommend', 'refer', 'reimburse', 'resolve', 'respond', 'submit', 'suggest', 'supervise', 'survey', 'validate'
]

prepositions = [
    'aboard', 'about', 'above', 'across', 'after', 'against', 'along', 'amid', 'among', 'around', 'as', 'at', 'before', 'behind', 'below', 'beneath', 'beside', 'between', 'beyond', 'but', 'by', 'concerning', 'considering', 'despite', 'down', 'during', 'except', 'for', 'from', 'in', 'inside', 'into',
    'like', 'near', 'of', 'off', 'on', 'onto', 'out', 'outside', 'over', 'past', 'regarding', 'round', 'since', 'through', 'to', 'toward', 'under', 'underneath', 'until', 'unto', 'up', 'upon', 'with', 'within', 'without']

articles = ["the", "a", "an"]

pronouns = ["I", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them", "my", "your", "his", "her", "its", "our", "their", "mine", "yours", "hers", "ours", "theirs", "this", "that", "these", "those", "who", "whom", "whose", "which", "what", "myself", "yourself", "himself", "herself", "itself", "ourselves", "themselves"]

conjunctions = ["and", "but", "or", "nor", "for", "so", "yet", "after", "although", "as", "because", "before", "even if", "even though", "if", "once", "since", "though", "unless", "until", "when", "where", "while"]

medical_keywords = insurance_claims_keywords + adjuster_note_keywords + verbs + prepositions + articles + pronouns + conjunctions