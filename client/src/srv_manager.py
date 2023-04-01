import srvlookup
from srvlookup import SRVQueryFailure


class SrvManager:
    @staticmethod
    def lookup(domain: str) -> (str, int):
        # TODO async implementation
        try:
            result = srvlookup.lookup("tt", "udp." + domain)
            print("SRV record found for domain: " + domain)
            print("Returning: " + result[0].host + ":" + str(result[0].port))
            return result[0].host, result[0].port
        except SRVQueryFailure as e:
            print("SRV record not found for domain: " + domain)
            print(e)
            return None, None
