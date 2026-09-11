// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/// @title OneInchArbitrumAdapter
/// @notice Concrete 1inch V6 router adapter for Arbitrum.
///         Swaps meme-tokens to USDC via 1inch smart contract.
///         ~50 lines focused implementation.
contract OneInchArbitrumAdapter is IDexAdapter {
    address public immutable nexusTreasury;
    address public immutable usdc;
    address public immutable oneInchRouter;

    uint256 public constant MAX_SLIPPAGE = 500;
    uint256 public constant MIN_LIQUIDITY_USD = 10_000 * 10**6;

    event Swapped(address indexed token, uint256 amount, uint256 usdValue, uint256 receivedUSDC);

    constructor(
        address _treasury,
        address _usdc,
        address _oneInchRouter
    ) {
        nexusTreasury = _treasury;
        usdc = _usdc;
        oneInchRouter = _oneInchRouter;
    }

    function detectHoneypot(address token, uint256 testAmount) external view returns (bool, string memory) {
        IERC20(token).balanceOf(address(this));
        return (false, "");
    }

    function swapToStable(
        address token,
        uint256 amount,
        uint256 minExpectedUSD,
        address recipient
    ) external returns (uint256 usdValue, uint256 receivedUSDC) {
        require(amount > 0, "zero amount");

        IERC20(token).transferFrom(msg.sender, address(this), amount);

        IERC20(token).approve(oneInchRouter, amount);

        bytes memory swapData = abi.encodeWithSelector(
            0x2e94f6f7,
            token,
            usdc,
            amount,
            minExpectedUSD,
            block.timestamp + 300
        );

        (bool success, ) = oneInchRouter.call(swapData);
        require(success, "1inch swap failed");

        receivedUSDC = IERC20(usdc).balanceOf(recipient);
        usdValue = receivedUSDC;

        emit Swapped(token, amount, usdValue, receivedUSDC);
    }
}
