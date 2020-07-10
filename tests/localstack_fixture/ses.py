import aioboto3

from .env import get_endpoint_url, get_region_name


class LocalSes(object):
    def __init__(self, endpoint_url=None, region_name=None):
        self.endpoint_url = endpoint_url or get_endpoint_url()
        self.region_name = region_name or get_region_name()

    async def create(self, spec):
        await self.load_config(config=spec)

    async def destroy(self, spec):
        pass

    def new_client(self):
        return aioboto3.client('ses', endpoint_url=self.endpoint_url, region_name=self.region_name)

    async def load_config(self, config):
        async with self.new_client() as client:
            response = client.list_identities()
            identities = response["Identities"]
            for identity in identities:
                await client.delete_identity(Identity=identity)

            verified_email_addresses = config.get("VerifiedEmailAddresses", [])
            for email_address in verified_email_addresses:
                await client.verify_email_address(EmailAddress=email_address)
            verified_email_identities = config.get("VerifiedEmailIdentities", [])
            for email_address in verified_email_identities:
                await client.verify_email_identity(EmailAddress=email_address)


"""
{
  "VerifiedEmailAddresses": ["me@example.com"],
  "VerifiedEmailIdentities": [ "..." ]
}
"""
