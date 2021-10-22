import struct

from constant.Constants import *


class BTP(object):
    def __init__(self, length, latitude, longitude):
        self.BTPType = ETSI_GN_NH_BTPB
        self.PktTransport = ETSI_GN_TRANSPORT_GEOBROADCAST
        self.TrafficClass = 0
        self.MaxPktLifetime = 0
        self.DestPort = BTP_PORT_DENM
        self.DestInfo = 0
        self.CommProfile = ETSI_GN_PROFILE_ITS_G5
        self.RepeatInterval = 0
        self.Length = length
        self.SecProfile = ETSI_GN_SEC_PROF_AID_SSP
        self.AID = 0x25
        self.SSPLen = 4
        self.SSPBits = [0x01, 0xFF, 0xFF, 0xFF, 0, 0]
        self.Latitude = latitude
        self.Longitude = longitude
        self.DistanceA = GN_GBC_DESTDISTANCEA
        self.DistanceB = GN_GBC_DESTDISTANCEB
        self.Shape = GN_GBC_DESTSHAPE
        self.Angle = GN_GBC_DESTANGLE
        self.Unused: int = UNUSED

    def assemble_btp_fields(self):
        temp = struct.pack('!BBBBHH',
                           self.BTPType,
                           self.PktTransport,
                           self.TrafficClass,
                           self.MaxPktLifetime,
                           self.DestPort,
                           self.DestInfo
                           )

        temp += struct.pack('!IIHHHBB',
                            self.Latitude,
                            self.Longitude,
                            self.DistanceA,
                            self.DistanceB,
                            self.Angle,
                            self.Shape,
                            self.Unused
                            )

        temp += struct.pack('!BBBBIBBBBBBH',
                            self.CommProfile,
                            self.RepeatInterval,
                            self.SecProfile,
                            self.SSPLen,
                            self.AID,
                            self.SSPBits[0],
                            self.SSPBits[1],
                            self.SSPBits[2],
                            self.SSPBits[3],
                            self.SSPBits[4],
                            self.SSPBits[5],
                            self.Length
                            )

        self.raw = temp
        return
