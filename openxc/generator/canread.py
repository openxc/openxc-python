#support functions

def ByteToHex( buff ):
    data = []
    for char in buff:
        data.append( "%02X" % ord( char ) )
    return ''.join( data ).strip()


def findEndBit(startBit, numBits):
    endBit = (startBit + numBits) % 8
    if 0 == endBit:
        return 8
    else:
        return endBit


def bitmask(numBits):
    return (0x1 << numBits) - 1


def startingByte(startBit):
    return startBit / 8


def endingByte(startBit, numBits):
    return (startBit + numBits - 1) / 8


def getBitField(data, startBit, numBits):

    startByte = startingByte(startBit)
    endByte = endingByte(startBit, numBits)

    ret = ord(data[startByte])
    if(startByte != endByte):
        # The lowest byte address contains the most significant bit.
        for i in range(startByte + 1, endByte+1):
            ret = ret << 8
            ret = ret | ord(data[i])

    ret = ret >> (8 - findEndBit(startBit, numBits))
    return ret & bitmask(numBits)


def decodeSignal(signal, data):
    rawValue = getBitField(data, signal['bit_position'], signal['bit_size'])
    return rawValue * signal['factor'] + signal['offset']


def ignoreHandler(signal, value):
    return ''


def stateHandler(signal, value):
    for state in signal['states']:
        if state['value'] == value:
            return sendJSONMessage(signal['generic_name'], state['name'])
    return ''


def booleanHandler(signal, value):
    if value == 0:
        return sendJSONMessage(signal['generic_name'], 'False')
    else:
        return sendJSONMessage(signal['generic_name'], 'True')


def floatHandler(signal, value):
    return sendJSONMessage(signal['generic_name'], str(value))


def booleanWriter(signal, value):
    return ''


def translateSignal(signal, data):
    value, send = preTranslate(signal, data)

    if send:
        signal['lastValue'] = value

    if signal['handler'] != None:
        return signal['handler'](signal, value)

    else:
        return floatHandler(signal, value)


def sendJSONMessage(name, value):
    return '{"name":"%s","value":%s}' % (name, value)


def preTranslate(signal, data):
    send = True
    value = decodeSignal(signal, data)

    if not signal['received'] or signal['sendClock'] == signal['frequency'] - 1:
        if send and (not signal['received'] or signal['send_same'] or value != signal['lastValue']):
            signal['received'] = True
        else:
            send = False

        signal['sendClock'] = 0
    else:
        send = False
        signal['sendClock'] = signal['sendClock'] + 1

    return value, send
