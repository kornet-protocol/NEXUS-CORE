// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.20;

/// @title IDEXAdapter
/// @notice Minimal DEX adapter interface for PurgeContract.
///         Production implementation should integrate 1inch, Uniswap V3, or Jupiter.
interface IDEXAdapter {
    function detectHoneypot(address token, uint256 testAmount) external returns (bool honeypot, string memory reason);
    function swapToStable(
        address token,
        uint256 amount,
        uint256 minExpectedUSD,
        address recipient
    ) external returns (uint256 usdValue, uint256 receivedUSDC);
}
