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
    # Ticket Detection
    # ======================================

    # 1. Incident ID
    ticket = re.search(

        r"Incident\s*ID\s*:\s*(INC\d+)",

        text,

        re.IGNORECASE

    )

    # 2. Ticket:
    if not ticket:

        ticket = re.search(

            r"Ticket\s*:\s*(TT\d+)",

            text,

            re.IGNORECASE

        )

    # 3. TTxxxxxxxx
    if not ticket:

        ticket = re.search(

            r"\b(TT\d{12})\b",

            text,

            re.IGNORECASE

        )

    if ticket:

        result["ticket"] = ticket.group(1).upper()


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
    # Circuit Detection
    # ======================================

    # 1. หา Circuit: โดยตรงก่อน
    # รองรับ เช่น
    # Circuit: V00613A
    # Circuit: I84641A

    circuit = re.search(

        r"(?im)^\s*Circuit\s*:\s*([A-Za-z0-9]+)",

        text

    )

    if circuit:

        result["circuit"] = circuit.group(1).upper()


    # 2. ถ้าไม่มี Circuit: ค่อยใช้รูปแบบเก่า
    else:

        circuit_patterns = [

            # WDS51358
            r"\b(WDS\d{4,8})\b",

            # V12345B / I12345B / U12345B / O12345B
            r"\b([VIUOJ]\d{4,8}B)\b",

            # J03429 / J03429B
            r"\b(J\d{4,8}B?)\b"

        ]


        for pattern in circuit_patterns:

            circuit = re.search(

                pattern,

                text,

                re.IGNORECASE

            )

            if circuit:

                result["circuit"] = circuit.group(1).upper()

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
Ticket: TT202608164574
FaultDate: 10/08/26 03:10
Circuit: V00613A
"""
    print(parse_sms(sms))