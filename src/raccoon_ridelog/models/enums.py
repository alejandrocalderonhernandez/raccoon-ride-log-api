import enum

class MotorcycleBrand(str, enum.Enum):
    TRIUMPH = "TRIUMPH"
    KAWASAKI = "KAWASAKI"
    SUZUKI = "SUZUKI"
    YAMAHA = "YAMAHA"
    OTHER = "OTHER"


class RiderRole(str, enum.Enum):
    ADMIN = "ADMIN"
    STANDARD_RIDER = "STANDARD_RIDER"