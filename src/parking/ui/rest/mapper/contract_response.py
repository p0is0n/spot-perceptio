from parking.application.dto.contract.spot import ParkingSpot, Spot
from parking.application.dto.contract.vehicle import Vehicle, VehicleDetails
from parking.ui.rest.response.analyze_spot import AnalyzeSpotResponse
from parking.ui.rest.response.spot import ParkingSpotResponse, SpotResponse
from parking.ui.rest.response.vehicle import VehicleDetailsResponse, VehicleResponse
from parking.ui.rest.response.plate import PlateResponse

class ContractResponseMapper:
    def make_analyze_spot(
        self,
        parking_spot: ParkingSpot,
        /
    ) -> AnalyzeSpotResponse:
        return AnalyzeSpotResponse(
            parking_spot=self.make_parking_spot(parking_spot)
        )

    def make_parking_spot(
        self,
        parking_spot: ParkingSpot,
        /
    ) -> ParkingSpotResponse:
        spot = self.make_spot(parking_spot.spot)
        vehicle = None
        if parking_spot.vehicle:
            vehicle = self.make_vehicle(parking_spot.vehicle)

        return ParkingSpotResponse(
            occupied=parking_spot.occupied,
            spot=spot,
            vehicle=vehicle
        )

    def make_spot(
        self,
        spot: Spot,
        /
    ) -> SpotResponse:
        return SpotResponse(
            id=spot.id
        )

    def make_vehicle(
        self,
        vehicle: Vehicle,
        /
    ) -> VehicleResponse:
        details = self.make_vehicle_details(vehicle.details)
        plate = None
        if vehicle.plate is not None:
            plate = self.make_plate(vehicle.plate.value, vehicle.plate.country)

        return VehicleResponse(
            details=details,
            plate=plate
        )

    def make_vehicle_details(
        self,
        details: VehicleDetails,
        /
    ) -> VehicleDetailsResponse:
        return VehicleDetailsResponse(
            type=details.type,
            color=details.color
        )

    def make_plate(
        self,
        value: str,
        country: str,
        /
    ) -> PlateResponse:
        return PlateResponse(
            value=value,
            country=country
        )
