class ServiceError(Exception): pass


class DuplicateError(ServiceError): pass


class NotFoundError(ServiceError): pass


class FailedCreateError(ServiceError): pass


class ExcessiveFrequency(ServiceError): pass
