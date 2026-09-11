import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(relative_path: str, module_name: str):
    path = ROOT / relative_path
    parent_dir = str(path.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GenesisSecurityBoundaryTests(unittest.TestCase):
    def test_unverified_inputs_are_rejected(self):
        module = load_module("core-engine/genesis_protocol.py", "genesis_protocol")
        protocol = module.GenesisProtocol()

        result = protocol.verify_and_mint_zkp(
            user_zk_proof=b"proof",
            action_type="tree_planted",
            hardware_signature="signature",
            network_nodes=["node-1"],
        )

        self.assertTrue(result.startswith("REJECTED:"))
        self.assertFalse(protocol.verify_zero_knowledge_identity(b"proof"))
        self.assertFalse(protocol.verify_hardware_root_of_trust("signature"))


class InfrastructureScanTests(unittest.TestCase):
    def test_missing_hardware_signatures_are_pending(self):
        module = load_module(
            "validators/infrastructure_scan.py", "infrastructure_scan"
        )
        validator = module.InfrastructureScan()

        result = validator.verify_proof_of_build([], [], "bim-hash")

        self.assertEqual(result["status"], "PENDING")


class TrustBoundaryTests(unittest.TestCase):
    def test_web_of_trust_rejects_unconfigured_verifier(self):
        module = load_module("identity-zkp/web_of_trust.py", "web_of_trust")
        trust = module.WebOfTrust(min_endorsements=1)

        accepted, reason = trust.endorse("alice", "bob", "signature", "context")

        self.assertFalse(accepted)
        self.assertEqual(reason, "signature_verifier_unconfigured")
        self.assertFalse(trust.is_human("bob"))

    def test_assembly_requires_signature_verifier(self):
        module = load_module("core-engine/proof_of_assembly.py", "proof_of_assembly")
        guild = module.AssemblyGuild()
        bom_hash = guild.compute_bom_hash(["atecc608a", "esp32"])
        guild.register_bom(bom_hash)

        result = guild.verify_assembly("device-1", "signature", "attestation", bom_hash)

        self.assertTrue(result.startswith("REJECTED:"))


if __name__ == "__main__":
    unittest.main()
