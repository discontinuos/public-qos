
class Codes:
    R_EMPTY     = 0xFF

    R_200_OK = 0x01
    R_OFFLINE   = 0x02
    R_ERROR     = 0x03
    R_TIMEOUT   = 0x04
    R_CONNECTION_CLOSED   = 0x05
    
    R_302_NOT_FOUND = 32

    R_400_BAD_REQUEST = 40
    R_401_UNAUTHORIZED = 41
    R_403_FORBIDDEN = 43
    R_404_NOT_FOUND = 44
    R_405_METHOD_NOT_ALLOWED = 45
    
    R_410_GONE = 42
    R_500_INTERNAL_SERVER_ERROR = 50
    R_503_SERVICE_UNAVAILABLE = 53
    R_550_PERMISSION_DENIED = 55

    def CodeToString(code):
        switcher = {
            Codes.R_EMPTY: 'Empty',
            Codes.R_OFFLINE: 'NO_NETWORK',
            Codes.R_TIMEOUT: 'TIMEOUT',
            Codes.R_CONNECTION_CLOSED: 'CONNECTION_CLOSED',
            Codes.R_ERROR: 'GENERIC_ERROR',
            Codes.R_200_OK: 'HTTP_200_OK',
            Codes.R_302_NOT_FOUND: 'HTTP_302_NOT_FOUND',
            Codes.R_400_BAD_REQUEST: 'HTTP_400_BAD_REQUEST',
            Codes.R_401_UNAUTHORIZED: 'HTTP_401_UNAUTHORIZED',
            Codes.R_403_FORBIDDEN: 'HTTP_403_FORBIDDEN',
            Codes.R_404_NOT_FOUND: 'HTTP_404_NOT_FOUND',
            Codes.R_410_GONE: 'HTTP_410_GONE',
            Codes.R_500_INTERNAL_SERVER_ERROR: 'HTTP_500_INTERNAL_SERVER_ERROR',
            Codes.R_503_SERVICE_UNAVAILABLE: 'HTTP_503_SERVICE_UNAVAILABLE',
            Codes.R_550_PERMISSION_DENIED: 'HTTP_550_PERMISSION_DENIED' }
        return switcher.get(code, 'Unrecognized code.' + str(code))

    def GetCodeFromHTTPStatus(httpCode):
        switcher = {
            200: Codes.R_200_OK,
            302: Codes.R_302_NOT_FOUND,
            400: Codes.R_400_BAD_REQUEST,
            401: Codes.R_401_UNAUTHORIZED,
            403: Codes.R_403_FORBIDDEN,
            404: Codes.R_404_NOT_FOUND,
            410: Codes.R_410_GONE,
            500: Codes.R_500_INTERNAL_SERVER_ERROR,
            503: Codes.R_503_SERVICE_UNAVAILABLE,
            550: Codes.R_550_PERMISSION_DENIED
        }
        return switcher.get(int(httpCode), Codes.R_ERROR)