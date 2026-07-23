"""
=========================================
OT Note Pro v1.0 - Falcon
SMS Parser
=========================================
"""

import re


# ==========================================
# Parse SMS
# ==========================================

def parse_sms(text: str):

    result = {

        "ticket": "",
        "circuit": "",
        "fault_date": "",
        "start_time": ""

    }

    if not text:

        return result

    # --------------------------------------
    # Ticket
    # --------------------------------------

    ticket = re.search(

        r"Ticket\s*:\s*([A-Za-z0-9\-]+)",

        text,

        re.IGNORECASE

    )

    if ticket:

        result["ticket"] = ticket.group(1).strip()

    # --------------------------------------
    # Circuit
    # --------------------------------------

    circuit = re.search(

        r"Circuit\s*:\s*([A-Za-z0-9\-_]+)",

        text,

        re.IGNORECASE

    )

    if circuit:

        result["circuit"] = circuit.group(1).strip()

    # --------------------------------------
    # Fault Date + Start Time
    # --------------------------------------

    fault = re.search(

        r"FaultDate\s*:\s*([0-9]{2}/[0-9]{2}/[0-9]{2})\s+([0-9]{2}:[0-9]{2})",

        text,

        re.IGNORECASE

    )

    if fault:

        result["fault_date"] = fault.group(1)

        result["start_time"] = fault.group(2)

    return result


# ==========================================
# Test Parser
# ==========================================

if __name__ == "__main__":

    sms = """
ช่าง Phuwanai Sopradit FIELD (Technician Corp) กดรับงาน

Ticket: TT202607179598

Subject: IP-DID | V96474B | Ping failure

FaultDate: 11/07/26 10:43

Circuit: V96474B

Customer: Test
"""

    print(parse_sms(sms))