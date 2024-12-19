def _lookup(table: dict[str | None, str], key: str) -> str:
    return table[key] if key in table else table[None] + f" ({key})"

license_statuses = {
    'A': 'Active',
    'C': 'Canceled',
    'E': 'Expired',
    'L': 'Pending Legal Status',
    'P': 'Parent Station Canceled',
    'T': 'Terminated',
    'X': 'Term Pending',
    None: 'Unknown License Status'
}

def license_status(code: str) -> str:
    return _lookup(license_statuses, code)

applicant_types = {
    'B': 'Amateur Club',
    'C': 'Corporation',
    'D': 'General Partnership',
    'E': 'Limited Partnership',
    'F': 'Limited Liability Partnership',
    'G': 'Governmental Entity',
    'H': 'Other',
    'I': 'Individual',
    'J': 'Joint Venture',
    'L': 'Limited Liability Company',
    'M': 'Military Recreation',
    'O': 'Consortium',
    'P': 'Partnership',
    'R': 'RACES',
    'T': 'Trust',
    'U': 'Unincorporated Association',
    None: 'Unknown Applicant Type'
}

def applicant_type(code: str) -> str:
    return _lookup(applicant_types, code)

operator_classes = {
    'A': 'Advanced',
    'E': 'Amateur Extra',
    'G': 'General',
    'N': 'Novice',
    'P': 'Technician Plus',
    'T': 'Technician',
    None: 'Unknown Operator Class'
}

def operator_class(code: str) -> str:
    return _lookup(operator_classes, code)
