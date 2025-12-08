from shared.domain.vo.coordinate import Coordinate, BoundingBox, Polygon
from shared.domain.aggregate.spot import Spot

from parking.domain.vo.plate import Plate
from parking.domain.aggregate.vehicle import Vehicle, VehicleDetails
from parking.domain.aggregate.spot import ParkingSpot
from parking.application.dto import contract

class ContractFactory:
    def make_parking_spot(self, parking_spot: ParkingSpot, /) -> contract.ParkingSpot:
        spot = self.make_spot(parking_spot.spot)
        vehicle = None
        if parking_spot.vehicle is not None:
            vehicle = self.make_vehicle(parking_spot.vehicle)

        return contract.ParkingSpot(
            occupied=parking_spot.occupied,
            spot=spot,
            vehicle=vehicle
        )

    def make_spot(self, spot: Spot, /) -> contract.Spot:
        coordinate = self.make_polygon_coordinate(spot.coordinate)

        return contract.Spot(
            id=spot.id.value,
            coordinate=coordinate
        )

    def make_coordinate(self, coordinate: Coordinate, /) -> contract.Coordinate:
        return contract.Coordinate(
            x=coordinate.x,
            y=coordinate.y
        )

    def make_bounding_box_coordinate(self, coordinate: BoundingBox, /) -> contract.BoundingBox:
        return contract.BoundingBox(
            p1=self.make_coordinate(coordinate.p1),
            p2=self.make_coordinate(coordinate.p2)
        )

    def make_polygon_coordinate(self, coordinate: Polygon, /) -> contract.Polygon:
        return contract.Polygon(
            corners=tuple(self.make_coordinate(corner) for corner in coordinate.corners)
        )

    def make_vehicle(self, vehicle: Vehicle, /) -> contract.Vehicle:
        vehicle_details = self.make_vehicle_details(vehicle.details)
        plate = None
        if vehicle.plate is not None:
            plate = self.make_plate(vehicle.plate)

        return contract.Vehicle(
            details=vehicle_details,
            plate=plate,
            coordinate=self.make_polygon_coordinate(vehicle.coordinate)
        )

    def make_vehicle_details(self, vehicle_details: VehicleDetails, /) -> contract.VehicleDetails:
        return contract.VehicleDetails(
            type=vehicle_details.type,
            color=vehicle_details.color
        )

    def make_plate(self, plate: Plate, /) -> contract.Plate:
        return contract.Plate(
            value=plate.value,
            country=plate.country,
            coordinate=self.make_polygon_coordinate(plate.coordinate)
        )
