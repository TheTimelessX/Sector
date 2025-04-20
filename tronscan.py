from httpx import AsyncClient, Response

class TronscanClient(object):
    def __init__(self):
        self.url = "https://apilist.tronscanapi.com/api/transaction-info?hash={}"
        self.http = AsyncClient()

    async def getInfo(self, hash: str) -> Response: return await self.http.get(self.url.format(hash))

    async def isMatch(self, results: dict, amount: int, wallet: str) -> bool:
        if "toAddress" in results:
            if results['toAddress'] == wallet:
                if results['VALUE'] >= amount: True
                else: return False
            else: return False

from rich import print
import asyncio
tc = TronscanClient()

d = asyncio.run(tc.getInfo('3705fc85cefaab4fe09b467cdbaa2a0d9a338adb76478e3943fab0adc7f90250'))
print(d.json())