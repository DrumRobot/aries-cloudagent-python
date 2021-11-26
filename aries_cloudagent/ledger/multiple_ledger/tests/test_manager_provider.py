from asynctest import TestCase as AsyncTestCase, mock as async_mock

from aries_cloudagent.indy.sdk.profile import IndySdkProfile

from ....askar.profile import AskarProfileManager
from ....config.injection_context import InjectionContext
from ....core.in_memory import InMemoryProfile
from ....indy.sdk.wallet_setup import IndyOpenWallet, IndyWalletConfig
from ....ledger.indy import IndySdkLedgerPool

from ..base_manager import MultipleLedgerManagerError
from ..manager_provider import MultiIndyLedgerManagerProvider

LEDGER_CONFIG = [
    {
        "id": "sovrinStaging",
        "is_production": True,
        "is_write": True,
        "genesis_transactions": {
            "reqSignature": {},
            "txn": {
                "data": {
                    "data": {
                        "alias": "Node1",
                        "blskey": "4N8aUNHSgjQVgkpm8nhNEfDf6txHznoYREg9kirmJrkivgL4oSEimFF6nsQ6M41QvhM2Z33nves5vfSn9n1UwNFJBYtWVnHYMATn76vLuL3zU88KyeAYcHfsih3He6UHcXDxcaecHVz6jhCYz1P2UZn2bDVruL5wXpehgBfBaLKm3Ba",
                        "blskey_pop": "RahHYiCvoNCtPTrVtP7nMC5eTYrsUA8WjXbdhNc8debh1agE9bGiJxWBXYNFbnJXoXhWFMvyqhqhRoq737YQemH5ik9oL7R4NTTCz2LEZhkgLJzB3QRQqJyBNyv7acbdHrAT8nQ9UkLbaVL9NBpnWXBTw4LEMePaSHEw66RzPNdAX1",
                        "client_ip": "192.168.65.3",
                        "client_port": 9702,
                        "node_ip": "192.168.65.3",
                        "node_port": 9701,
                        "services": ["VALIDATOR"],
                    },
                    "dest": "Gw6pDLhcBcoQesN72qfotTgFa7cbuqZpkX3Xo6pLhPhv",
                },
                "metadata": {"from": "Th7MpTaRZVRYnPiabds81Y"},
                "type": "0",
            },
            "txnMetadata": {
                "seqNo": 1,
                "txnId": "fea82e10e894419fe2bea7d96296a6d46f50f93f9eeda954ec461b2ed2950b62",
            },
            "ver": "1",
        },
    },
    {
        "id": "sovrinTest",
        "is_production": False,
        "genesis_transactions": {
            "reqSignature": {},
            "txn": {
                "data": {
                    "data": {
                        "alias": "Node1",
                        "blskey": "4N8aUNHSgjQVgkpm8nhNEfDf6txHznoYREg9kirmJrkivgL4oSEimFF6nsQ6M41QvhM2Z33nves5vfSn9n1UwNFJBYtWVnHYMATn76vLuL3zU88KyeAYcHfsih3He6UHcXDxcaecHVz6jhCYz1P2UZn2bDVruL5wXpehgBfBaLKm3Ba",
                        "blskey_pop": "RahHYiCvoNCtPTrVtP7nMC5eTYrsUA8WjXbdhNc8debh1agE9bGiJxWBXYNFbnJXoXhWFMvyqhqhRoq737YQemH5ik9oL7R4NTTCz2LEZhkgLJzB3QRQqJyBNyv7acbdHrAT8nQ9UkLbaVL9NBpnWXBTw4LEMePaSHEw66RzPNdAX1",
                        "client_ip": "192.168.65.3",
                        "client_port": 9702,
                        "node_ip": "192.168.65.3",
                        "node_port": 9701,
                        "services": ["VALIDATOR"],
                    },
                    "dest": "Gw6pDLhcBcoQesN72qfotTgFa7cbuqZpkX3Xo6pLhPhv",
                },
                "metadata": {"from": "Th7MpTaRZVRYnPiabds81Y"},
                "type": "0",
            },
            "txnMetadata": {
                "seqNo": 1,
                "txnId": "fea82e10e894419fe2bea7d96296a6d46f50f93f9eeda954ec461b2ed2950b62",
            },
            "ver": "1",
        },
    },
]


class TestMultiIndyLedgerManagerProvider(AsyncTestCase):
    async def test_provide_invalid_manager(self):
        profile = InMemoryProfile.test_profile()
        provider = MultiIndyLedgerManagerProvider(profile)
        context = InjectionContext()
        context.settings["ledger.ledger_config_list"] = LEDGER_CONFIG
        with self.assertRaises(MultipleLedgerManagerError):
            provider.provide(context.settings, context.injector)

    async def test_provide_indy_manager(self):
        context = InjectionContext()
        context.injector.bind_instance(IndySdkLedgerPool, IndySdkLedgerPool("name"))
        profile = IndySdkProfile(
            IndyOpenWallet(
                config=IndyWalletConfig({"name": "test-profile"}),
                created=True,
                handle=1,
                master_secret_id="master-secret",
            ),
            context,
        )
        provider = MultiIndyLedgerManagerProvider(profile)
        context.settings["ledger.ledger_config_list"] = LEDGER_CONFIG
        self.assertEqual(
            provider.provide(context.settings, context.injector).__class__.__name__,
            "MultiIndyLedgerManager",
        )

    async def test_provide_askar_manager(self):
        context = InjectionContext()
        profile = await AskarProfileManager().provision(
            context,
            {
                # "auto_recreate": True,
                # "auto_remove": True,
                "name": ":memory:",
                "key": await AskarProfileManager.generate_store_key(),
                "key_derivation_method": "RAW",  # much faster than using argon-hashed keys
            },
        )
        provider = MultiIndyLedgerManagerProvider(profile)
        context.settings["ledger.ledger_config_list"] = LEDGER_CONFIG
        self.assertEqual(
            provider.provide(context.settings, context.injector).__class__.__name__,
            "MultiIndyVDRLedgerManager",
        )
