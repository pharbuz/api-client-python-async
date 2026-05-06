import builtins

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient


class GeoRegionsIpAddressMappingsService:
    ENDPOINT = "/api/config/v1/geographicRegions/ipAddressMappings"

    def __init__(self, http_client: HttpClient):
        self._http_client = http_client

    async def list(self) -> "IPAddressMapping":
        """
        Lists all IP address mappings of the environment
        """
        response = (await self._http_client.make_request(self.ENDPOINT)).json()
        return IPAddressMapping(self._http_client, None, response)

    async def put(self, mappings: builtins.list["IPAddressMapping"]):
        """
        Updates the IP address mappings of the environment
        """
        data = [mapping.json() for mapping in mappings]
        body = {"ipAddressMappingRules": data}
        (await self._http_client.make_request(self.ENDPOINT, method="PUT", params=body))


class IPAddressMapping(DynatraceObject):
    def _create_from_raw_data(self, raw_element):
        self.rules: list[IPAddressMappingRule] = [
            IPAddressMappingRule(raw_element=e)
            for e in raw_element.get("ipAddressMappingRules")
        ]


class IPAddressMappingRule(DynatraceObject):
    def _create_from_raw_data(self, raw_element):
        self.location = IPAddressMappingLocation(
            raw_element=raw_element.get("location")
        )
        self.ip_range = IPAddressRange(raw_element=raw_element.get("ipRange"))

    @staticmethod
    def create(location: "IPAddressMappingLocation", ip_range: "IPAddressRange"):
        """
        Creates a new IP address mapping rule
        """
        return IPAddressMappingRule(
            raw_element={
                "ipAddressMappingLocation": location.json(),
                "ipAddressRange": ip_range.json(),
            }
        )


class IPAddressMappingLocation(DynatraceObject):
    def _create_from_raw_data(self, raw_element):
        self.country_code: str = raw_element.get("countryCode")
        self.city: str | None = raw_element.get("city")
        self.region_code: str | None = raw_element.get("regionCode")
        self.latitude: float | None = raw_element.get("latitude")
        self.longitude: float | None = raw_element.get("longitude")

    @staticmethod
    def create(
        country_code: str,
        city: str | None = None,
        region_code: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
    ):
        return IPAddressMappingLocation(
            raw_element={
                "countryCode": country_code,
                "city": city,
                "regionCode": region_code,
                "latitude": latitude,
                "longitude": longitude,
            },
        )


class IPAddressRange(DynatraceObject):
    def _create_from_raw_data(self, raw_element):
        self.address: str = raw_element.get("address")
        self.subnet_mask: int | None = raw_element.get("subnetMask")
        self.address_to: str | None = raw_element.get("addressTo")

    @staticmethod
    def create(
        address: str, subnet_mask: int | None = None, address_to: str | None = None
    ) -> "IPAddressRange":
        return IPAddressRange(
            raw_element={
                "address": address,
                "subnetMask": subnet_mask,
                "addressTo": address_to,
            }
        )
