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

    # 1. Incident ID / Ticket Label
    ticket = re.search(

        r"(?:Incident\s*ID|Ticket)\s*:\s*(INC\d+|TT\d+)",

        text,

        re.IGNORECASE

    )

    # 2. INCxxxxxxxxxxxx / TTxxxxxxxxxxxx (จับรหัสลอยๆ)
    if not ticket:

        ticket = re.search(

            r"\b(INC\d+|TT\d+)\b",

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

        r"((?:TT|INC)\d+)\s+([A-Z]{1,5}\d+[A-Z0-9]*)\s+(\d{2}/\d{2}/\d{2,4})\s+(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})",

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

    # 1. หา Circuit: หรือ IP DID: โดยตรงก่อน
    circuit = re.search(

        r"(?im)^\s*(?:Circuit|IP\s*DID)\s*:\s*([A-Za-z0-9]+)",

        text

    )

    if circuit:

        result["circuit"] = circuit.group(1).upper()


    # 2. ถ้าไม่มี Prefix ค้นหาจากรูปแบบรหัส Circuit โดยตรง (รองรับส่งรหัสมาลอยๆ)
    else:

        circuit_patterns = [

            # WDS51238 / WDS51358
            r"\b(WDS\d{4,8})\b",

            # I83948B, I83948A, V59973B, V59973A, J03429, J03429B, U..., O...
            # รองรับทั้งแบบลงท้ายด้วย A/B หรือไม่มีอักษรต่อท้าย
            r"\b([IVJUO]\d{4,8}[A-Z]?)\b"

        ]


        for pattern in circuit_patterns:

            circuit = re.search(

                pattern,

                text,

                re.IGNORECASE

            )

            if circuit:

                found_code = circuit.group(1).upper()

                # กันไม่ให้ดึงสับสนกับ Ticket (เผื่อหลุดมา)
                if not found_code.startswith(("TT", "INC")):

                    result["circuit"] = found_code

                    break



    # ======================================
    # Fault Date
    # ======================================

    fault = re.search(

        r"FaultDate\s*:\s*([0-9]{2}/[0-9]{2}/[0-9]{2,4})\s+([0-9]{2}:[0-9]{2})",

        text,

        re.IGNORECASE

    )


    if fault:

        result["fault_date"] = fault.group(1)

        result["start_time"] = fault.group(2)


    else:


        for line in lines:


            if re.match(

                r"^\d{2}/\d{2}/\d{2,4}$",

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
INC000102894106
J03429
10/08/26 03:10
"""
    print(parse_sms(sms))