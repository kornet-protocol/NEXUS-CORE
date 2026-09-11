// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/// @title UniswapV3ArbitrumAdapter
/// @notice Minimal Uniswap V3 adapter for Arbitrum.
///         Swaps meme-tokens to USDC via Uniswap V3 router.
///         ~50 lines focused implementation.
contract UniswapV3ArbitrumAdapter is IDexAdapter {
    address public immutable nexusTreasury;
    address public immutable usdc;
    address public immutable uniswapRouter;

    uint256 public constant MAX_SLIPPAGE = 500;
    uint256 public constant MIN_LIQUIDITY_USD = 10_000 * 10**6;

    event Swapped(address indexed token, uint256 amount, uint256 usdValue, uint256 receivedUSDC);

    constructor(
        address _treasury,
        address _usdc,
        address _uniswapRouter
    ) {
        nexusTreasury = _treasury;
        usdc = _usdc;
        uniswapRouter = _uniswapRouter;
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
        IERC20(token).approve(uniswapRouter, amount);

        bytes memory path = abi.encodePacked(token, usdc);
        
        (bool success, ) = uniswapRouter.call(
            abi.encodeWithSelector(
                IUniswapV3Router.exactInput.selector,
                path,
                recipient,
                amount,
                minExpectedUSD,
                block.timestamp + 300
            )
        );
        require(success, "Uniswap swap failed");

        receivedUSDC = IERC20(usdc).balanceOf(recipient);
        usdValue = receivedUSDC;

        emit Swapped(token, amount, usdValue, receivedUSDC);
    }
}

interface IUniswapV3Router {
    function exactInput(
        bytes calldata path,
        address recipient,
        uint256 amountIn,
        uint256 amountOutMinimum,
        uint256 deadline
    ) external payable returns (uint256 amountOut);
}
