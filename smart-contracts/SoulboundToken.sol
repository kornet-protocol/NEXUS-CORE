# SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.20;

contract NexusSoulboundStatus {
    string public name = "NEXUS Soulbound Status";
    string public symbol = "NSS";

    address public immutable genesisProtocol;
    uint256 public constant BPS_DENOMINATOR = 10000;
    uint256 public constant DEFAULT_DAILY_DECAY_BPS = 5;

    struct UserKarma {
        uint256 baseAmount;
        uint256 lastUpdated;
    }

    mapping(address => UserKarma) private _karma;

    event StatusUpdated(address indexed human, uint256 newKarma);

    constructor(address _genesis) {
        require(_genesis != address(0), "Invalid genesis");
        genesisProtocol = _genesis;
    }

    modifier onlyGenesis() {
        require(msg.sender == genesisProtocol, "NEXUS: Only Genesis Protocol");
        _;
    }

    function mintStatus(address to, uint256 amount) external onlyGenesis {
        uint256 current = reputationOf(to);
        _karma[to] = UserKarma({
            baseAmount: current + amount,
            lastUpdated: block.timestamp
        });
        emit StatusUpdated(to, _karma[to].baseAmount);
    }

    function reputationOf(address account) public view returns (uint256) {
        UserKarma memory record = _karma[account];
        if (record.baseAmount == 0) return 0;

        uint256 elapsedDays = (block.timestamp - record.lastUpdated) / 1 days;
        if (elapsedDays == 0) return record.baseAmount;

        uint256 totalDecayBps = elapsedDays * DEFAULT_DAILY_DECAY_BPS;
        if (totalDecayBps >= BPS_DENOMINATOR) {
            return 0;
        }

        uint256 decayAmount = (record.baseAmount * totalDecayBps) / BPS_DENOMINATOR;
        return record.baseAmount - decayAmount;
    }

    function transfer(address, uint256) external pure returns (bool) {
        revert("NEXUS: Soulbound tokens are strictly non-transferable");
    }
}
