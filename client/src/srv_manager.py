import srvlookup
from srvlookup import SRVQueryFailure
from dns.resolver import LifetimeTimeout


class SrvManager:
    @staticmethod
    def lookup(domain: str) -> (str, int):
        # TODO async implementation
        try:
            result = srvlookup.lookup("tt", "udp", domain)
            print("SRV record found for domain: " + domain)
            print("Returning: " + result[0].host + ":" + str(result[0].port))
            return result[0].host, result[0].port
        except LifetimeTimeout as timeout_error:
            print("SRV query timeout:")
            print(timeout_error)
            return None, None
        except SRVQueryFailure as e:
            print("SRV record not found for domain: " + domain)
            print(e)
            return None, None
