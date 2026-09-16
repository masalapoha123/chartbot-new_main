import regex



def extract_deliver_ID(userQuery):
    match = regex.search(r"\bDEL\d+\b", userQuery, regex.IGNORECASE)

    if match:
        return match.group(0).upper()

    return None


def extract_complaint_ID(userQuery):
    match = regex.search(r"\bCOM\d+\b", userQuery, regex.IGNORECASE)

    if match:
        return match.group(0).upper()

    return None