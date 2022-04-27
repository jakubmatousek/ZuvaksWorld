"""Zde skladuji me vlastni chybove hlasky"""

class baseImgNotCreated(Exception):
    pass

class logicError(Exception):
    pass

class WorkerError(Exception):
    pass

class notAProbabiltyError():
    pass
class FileError():
    pass

#-----------------------#
class badPasswordError(Exception):
    pass

class badUsernameError(Exception):
    pass


class FileNotFoundError(Exception):
    pass

class badCredentialsError(Exception):
    pass

class BadFileFormatError(Exception):
    pass

class loginError(Exception):
    pass

class BadConnectionInfo(Exception):
    pass

class connectionError(Exception):
    pass

class collectionEmptyError(Exception):
    pass

class UserNotAuthorizedError(Exception):
    pass

class invalidFontSizeError(Exception):
    pass

class bannerError(Exception):
    pass 

class not_valid_RGB(Exception):
    pass 

class FileError(Exception):
    pass