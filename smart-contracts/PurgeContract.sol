// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";

/// @title IDexAdapter
/// @notice External adapter interface for DEX aggregation and honeypot detection.
///         Production deployments should implement this with 1inch/0x/Jupiter or similar.
interface IDexAdapter {
    function detectHoneypot(address token, uint256 testAmount) external returns (bool honeypot, string memory reason);
    function swapToStable(
        address token,
        uint256 amount,
        uint256 minExpectedUSD,
        address recipient
    ) external returns (uint256 usdValue, uint256 receivedUSDC);
}

/// @title Purge Contract
/// @notice Контракт Очищения. Принимает мем-коины, генерирует ликвидность
///         через DEX-агрегацию и направляет средства на казначейство NEXUS.
contract PurgeContract is Ownable, ReentrancyGuard, Pausable {
    IERC20 public immutable usdc;
    IERC20 public immutable usdt;
    address public immutable foundingPurger;
    address public immutable nexusTreasury;
    IDexAdapter public dexAdapter;

    uint256 public constant MAX_SLIPPAGE = 500;
    uint256 public constant MIN_LIQUIDITY_USD = 10_000 * 10**6;
    uint256 public constant PURGE_COOLDOWN = 1 days;

    uint256 public totalPurgedVolume;
    uint256 public lastPurgeTimestamp;
    mapping(address => bool) public supportedTokens;
    mapping(address => mapping(address => uint256)) public tokenLastPurge;

    event TokenPurged(address indexed token, uint256 amount, uint256 usdValue, uint256 receivedUSDC);
    event TokenRejected(address indexed token, string reason);
    event TreasuryTopped(uint256 amount);
    event AdapterUpdated(address indexed oldAdapter, address indexed newAdapter);

    modifier onlyMultisig() {
        require(msg.sender == owner(), "Only multisig");
        _;
    }

    constructor(
        address _usdc,
        address _usdt,
        address _foundingPurger,
        address _treasury,
        address _dexAdapter,
        address _owner
    ) Ownable(_owner) {
        usdc = IERC20(_usdc);
        usdt = IERC20(_usdt);
        foundingPurger = _foundingPurger;
        nexusTreasury = _treasury;
        dexAdapter = IDexAdapter(_dexAdapter);
    }

    /// @notice Основной метод очищения: пользователь отправляет мем-коин
    function purgeToken(
        address token,
        uint256 amount,
        uint256 minExpectedUSD
    ) external nonReentrant whenNotPaused returns (uint256) {
        require(supportedTokens[token], "Token not supported");
        require(amount > 0, "Zero amount");
        require(
            block.timestamp >= tokenLastPurge[msg.sender][token] + PURGE_COOLDOWN,
            "Cooldown active"
        );

        IERC20(token).transferFrom(msg.sender, address(this), amount);

        (bool honeypot, string memory reason) = dexAdapter.detectHoneypot(token, amount / 1000);
        require(!honeypot, reason);

        (uint256 usdValue, uint256 receivedUSDC) = dexAdapter.swapToStable(
            token, amount, minExpectedUSD, nexusTreasury
        );

        totalPurgedVolume += usdValue;
        lastPurgeTimestamp = block.timestamp;
        tokenLastPurge[msg.sender][token] = block.timestamp;

        emit TokenPurged(token, amount, usdValue, receivedUSDC);

        return usdValue;
    }

    /// @notice Обновить DEX-адаптер (только multisig)
    function updateDexAdapter(address newAdapter) external onlyMultisig {
        require(newAdapter != address(0), "Invalid adapter");
        address old = address(dexAdapter);
        dexAdapter = IDexAdapter(newAdapter);
        emit AdapterUpdated(old, newAdapter);
    }

    /// @notice Добавить поддерживаемый мем-коин (только multisig)
    function addSupportedToken(address token) external onlyMultisig {
        supportedTokens[token] = true;
    }

    /// @notice Удалить токен (при обнаружении скама)
    function removeSupportedToken(address token) external onlyMultisig {
        supportedTokens[token] = false;
    }

    /// @notice Экстренная пауза (multisig)
    function pause() external onlyMultisig {
        _pause();
    }

    /// @notice Снятие паузы (multisig)
    function unpause() external onlyMultisig {
        _unpause();
    }

    /// @notice Получить текущие настройки контракта
    function getConfig() external view returns (
        uint256 totalVolume,
        uint256 lastPurge,
        uint256 supportedCount
    ) {
        totalVolume = totalPurgedVolume;
        lastPurge = lastPurgeTimestamp;
        supportedCount = 0;
    }
}
