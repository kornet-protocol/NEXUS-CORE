// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/// @title Founding Purger SBT
/// @notice Soulbound Token для участников Контракта Очищения.
///         Непередаваемый бейдж "Founding Purger".
contract FoundingPurger is ERC721, Ownable, ReentrancyGuard {
    uint256 public constant MAX_SUPPLY = 10_000;
    uint256 public constant PURGE_THRESHOLD = 100 * 10**18;
    uint256 public nextTokenId;
    uint256 public totalPurged;
    address public immutable nexusTreasury;
    mapping(address => bool) public hasPurged;
    mapping(uint256 => uint256) public purgeTimestamp;
    mapping(address => uint256) public purgeAmount;

    event Purged(address indexed user, uint256 tokenId, uint256 amount);
    event TreasuryFunded(uint256 amount);

    constructor(address _treasury) ERC721("Founding Purger", "PURGER") Ownable(msg.sender) {
        nexusTreasury = _treasury;
    }

    /// @notice Основной шлюз очищения: пользователь жертвует "мусорные" токены
    function purge(
        address tokenAddress,
        uint256 amount,
        uint256 minAccepted
    ) external nonReentrant returns (uint256) {
        require(!hasPurged[msg.sender], "Already purged");
        require(amount >= PURGE_THRESHOLD, "Below purge threshold");
        require(nextTokenId < MAX_SUPPLY, "Max supply reached");

        IERC20(tokenAddress).transferFrom(msg.sender, address(this), amount);
        uint256 received = IERC20(tokenAddress).balanceOf(address(this));
        require(received >= minAccepted, "Honeypot detected");

        uint256 tokenId = nextTokenId++;
        _safeMint(msg.sender, tokenId);

        hasPurged[msg.sender] = true;
        totalPurged += received;
        purgeAmount[msg.sender] = received;
        purgeTimestamp[tokenId] = block.timestamp;

        emit Purged(msg.sender, tokenId, received);
        return tokenId;
    }

    /// @notice Приоритетный доступ к озесисам для держателей Founding Purger
    function oasisPriorityMultiplier(address user) external view returns (uint256) {
        return hasPurged[user] ? 10 : 1;
    }

    /// @notice Вывод средств на казначейство NEXUS (только мультисиг)
    function fundTreasury(address tokenAddress, uint256 amount) external onlyOwner {
        IERC20(tokenAddress).transfer(nexusTreasury, amount);
        emit TreasuryFunded(amount);
    }

    /// @notice Soulbound override: only mint is allowed (from == address(0), to != address(0))
    function _beforeTokenTransfer(address from, address to, uint256 tokenId) internal override {
        require(from == address(0) && to != address(0), "Soulbound: non-transferable");
        super._beforeTokenTransfer(from, to, tokenId);
    }

    function supportsInterface(bytes4 interfaceId) public view override returns (bool) {
        return interfaceId == type(IERC165).interfaceId || super.supportsInterface(interfaceId);
    }
}
