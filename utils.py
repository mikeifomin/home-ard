def find_frame(buffer, signature_start="<SOF>", signature_end="<EOF>"):
    start_pos = buffer.find(signature_start)
    if start_pos < 0:
        return buffer, None

    end_pos = buffer.find(signature_end, start_pos)
    if end_pos < 0:
        return buffer, None

    frame = buffer[start_pos:end_pos]
    vars = frame.splitlines()
    end_of_string = "\n"
    vars = vars[1:]

    result = {}
    for var in vars:
        try:
            keyvalue = var.split(":")
            value = keyvalue[1].strip()
            key = keyvalue[0].strip()

            if value == "?":
                result[key] = None
            elif value.find(".") != -1:
                result[key] = float(value)
            else:
                result[key] = int(value)
        except (ValueError,):
            result[key] = value
        except (KeyError,IndexError):
            pass

    frame_start = start_pos
    frame_end = buffer.find(end_of_string, end_pos)
    buffer = (buffer[0:frame_start] + buffer[frame_end:]).strip()
    return buffer, result

def clear_buffer(buffer, signature_start="<SOF>", signature_end="<EOF>"):
    start_pos = buffer.find(signature_start)
    end_pos = buffer.find(signature_end)

    if start_pos < 0 and end_pos < 0:
        return ""
    else:
        return buffer

def find_all_frame(buffer, signature_start="<SOF>", signature_end="<EOF>"):
    results = []
    while True:
        buffer, result = find_frame(buffer, signature_start="<SOF>", signature_end="<EOF>")
        print(result)
        if result is None:
            break
        else:
            results.append(result)
    buffer = clear_buffer(buffer, signature_start="<SOF>", signature_end="<EOF>")
    return buffer, results

if __name__ == "__main__":
    data = """
<SOF>2347829
Temp0: 29.44
Temp1: 27.12
Temp2: 21.87
Temp3: ?
Temp4: 60.44
Temp5: 71.56
Temp6: 32.94
Temp7: 30.00
SetUpPol: 40.00
PolKp: 1000.00
PolKi: 1.00
PolKd: 1.00
PolSampleTime: 5000.00
dSetPointPol: 29.77
dInputPol: 29.44
OutputPol: 0.00
Skip: 0
<EOF>2347829

<SOF>6193
Temp0: 35.56
Temp1: 29.75
Temp2: 22.00
Temp3: 21.87
Temp4: 65.50
Temp5: 72.81
Temp6: 71.19
Temp7: 31.44
Message: measures ok. Calculating PID
SetUpPol: 40.00
PolKp: 1000.00
PolKi: 1.00
PolKd: 1.00
PolSampleTime: 5000.00
dSetPointPol: 35.70
dInputPol: 35.56
OutputPol: 138.88
Skip: 0
<EOF>6193


sdfs



    """
    print find_all_frame(data)