from dronekit import connect, LocationGlobalRelative, VehicleMode
import time
import math
import requests
import RestManager

class Drone():

    def __init__(self,connection_string = 'tcp:127.0.0.1:5760',altitude = 20):
        self.drone = connect(connection_string, wait_ready = True, baud = 57600)
        self.arm_and_takeoff(altitude)
        self.set_etat('STOP')
        self.id_intervention = 'test'
        self.RM = RestManager()

    def set_intervention(self,id_intervention):
        self.id_intervention = id_intervention

    def set_etat(self,etat):
        #pour le moment pas de vérifications
        self.etat = etat

    def is_AlreadyFlying(self):
        # pas armer si atteri
        # altitude par rapport a la position de depart, si elle est au dessus du sol
        if (self.drone.armed and self.drone.location.global_relative_frame.alt > 5):
            # deja en vol
            return True
        else:
            return False

    def aller_a(self,point,groundspeed=10):
        if not self.is_AlreadyFlying():
            self.arm_and_takeoff(20.5)
        if not groundspeed:
            self.drone.simple_goto(point)
        else:
            self.drone.simple_goto(point, groundspeed)

    def arm_and_takeoff(self,aTargetAltitude):
        while not self.drone.is_armable:
            print('waiting initialisation...')
            time.sleep(1)
        # Copter should arm in GUIDED mode
        self.drone.mode = VehicleMode("GUIDED")
        self.drone.armed = True

        # Confirm vehicle armed before attempting to take off
        while not self.drone.armed:
            print('waiting for arming...')
            time.sleep(1)
        print('taking off!')
        self.drone.simple_takeoff(aTargetAltitude)  # Take off to target altitude

        # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
        #  after Vehicle.simple_takeoff will execute immediately).
        while True:
            """print
            " Altitude: ", vehicule.location.global_relative_frame.alt"""
            # Break and return from function just below target altitude.
            if self.drone.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
                """print
                "Reached target altitude"""""
                break
            time.sleep(1)

    def setSpeed(self,speed):
        self.drone.airspeed = speed

    def setAltitude(self,alt):
        self.drone.location.global_relative_frame.alt = alt

    # Fonction to get the GPS location
    def getGPSCoordonate(self):
        return self.drone.location.global_frame

    def getGPSCoordonateRelatif(self):
        return self.drone.location.global_relative_frame

    def RTLandFinish(self):
        self.drone.mode = VehicleMode("RTL")
        self.drone.close()

    def attente_arrivee(self,destination):
        while get_distance_metres(self.getGPSCoordonate(),destination)>1:
            time.sleep(1)
        print('arrivée à destination :'+str(destination))

    def notifier_serveur_position(self):
        value = {}
        value['id_intervention'] = self.id_intervention
        position = self.getGPSCoordonate()
        value['position'] = [position.lat, position.lon]
        self.RM.post_position(value)
        #requests.post('http://148.60.11.238:8080/positiondrone',data = value)


def get_distance_metres(aLocation1, aLocation2):
    """
    Returns the ground distance in metres between two LocationGlobal objects.

    This method is an approximation, and will not be accurate over large distances and close to the
    earth's poles. It comes from the ArduPilot test code:
    https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
    """
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    dlong *= math.cos(aLocation2.lat * math.pi / 180.0)
    return math.sqrt((dlat * dlat) + (dlong * dlong)) * 1.113195e5