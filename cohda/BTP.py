import struct

import constants.Constants


class BTP(object):
    def __init__(self, length, latitude, longitude):
        self.BTPType = constants.Constants.ETSI_GN_NH_BTPB
        self.PktTransport = constants.Constants.ETSI_GN_TRANSPORT_GEOBROADCAST
        self.TrafficClass = 0
        self.MaxPktLifetime = 0
        self.DestPort = constants.Constants.BTP_PORT_DENM
        self.DestInfo = 0
        self.CommProfile = constants.Constants.ETSI_GN_PROFILE_ITS_G5
        self.RepeatInterval = 0
        self.Lenght = length
        self.SecProfile = constants.Constants.ETSI_GN_SEC_PROF_AID_SSP
        self.AID = 0x25
        self.SSPLen = 4
        self.SSPBits = [0x01, 0xFF, 0xFF, 0xFF, 0, 0]
        self.Latitude = latitude
        self.Longitude = longitude
        self.DistanceA = constants.Constants.GN_GBC_DESTDISTANCEA
        self.DistanceB = constants.Constants.GN_GBC_DESTDISTANCEB
        self.Shape = constants.Constants.GN_GBC_DESTSHAPE
        self.Angle = constants.Constants.GN_GBC_DESTANGLE
        self.Unused = 0
