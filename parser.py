"""
=========================================
OT Note Pro v1.1 - Falcon
SMS Parser v2
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
        "start_time": "",
        "finish_time": ""

    }


    if not text:

        return result


    lines = [
        x.strip()
        for x in text.splitlines()
        if x.strip()
    ]


    # ======================================
    # Ticket
    # ======================================

    ticket = re.search(

        r"Ticket\s*:\s*(TT\d+)",

        text,

        re.IGNORECASE

    )


    if ticket:

        result["ticket"] = ticket.group(1)


    else:

        for line in lines:

            if re.match(

                r"^TT\d+$",

                line,

                re.IGNORECASE

            ):

                result["ticket"] = line

                break


    # ======================================
    # Single Line Format
    # Ticket Circuit Date Time
    # ======================================

    single_line = re.search(

        r"(TT\d+)\s+([A-Z]{1,5}\d+[A-Z0-9]*)\s+(\d{2}/\d{2}/\d{2})\s+(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})",

        text,

        re.IGNORECASE

    )


    if single_line:

        result["ticket"] = single_line.group(1)

        result["circuit"] = single_line.group(2)

        result["fault_date"] = single_line.group(3)

        result["start_time"] = single_line.group(4)

        result["finish_time"] = single_line.group(5)

        return result


    # ======================================
    # Circuit
    # ======================================

    circuit = re.search(

        r"Circuit\s*:\s*([A-Z0-9]+)",

        text,

        re.IGNORECASE

    )


    if circuit:

        result["circuit"] = circuit.group(1).strip()


    else:

        for line in lines:

            line = line.strip()


            # ข้าม Ticket

            if line == result["ticket"]:
                continue


            # Circuit รูปแบบจริง
            # V96474B
            # I06217B
            # WDS52081
            # J03429

            if re.match(

                r"^[A-Z]{1,4}\d{3,8}[A-Z0-9]*$",

                line

            ):

                result["circuit"] = line

                break



    # ======================================
    # Fault Date
    # ======================================

    fault = re.search(

        r"FaultDate\s*:\s*([0-9]{2}/[0-9]{2}/[0-9]{2})\s+([0-9]{2}:[0-9]{2})",

        text,

        re.IGNORECASE

    )


    if fault:

        result["fault_date"] = fault.group(1)

        result["start_time"] = fault.group(2)


    else:


        for line in lines:


            if re.match(

                r"^\d{2}/\d{2}/\d{2}$",

                line

            ):

                result["fault_date"] = line

                break



    # ======================================
    # Start Finish
    # ======================================

    time_range = re.search(

        r"(\d{2}:\d{2})\s*[-]\s*(\d{2}:\d{2})",

        text

    )


    if time_range:

        result["start_time"] = time_range.group(1)

        result["finish_time"] = time_range.group(2)

    return result

# ==========================================
# Test Parser
# ==========================================

if __name__ == "__main__":


    sms = """
TT202607196530
WDS52081
13/07/26
19:00-21:30
"""


    print(parse_sms(sms))