// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

contract reentrancy000Safe {
    mapping(address => uint256) public balances;

    function deposit() external payable {
        require(msg.value > 0, "Value must be greater than 0");
        balances[msg.sender] += msg.value;
    }

    function getBalance(address user) external view returns (uint256) {
        return balances[user];
    }

    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        balances[msg.sender] -= amount;
        (bool sent, ) = msg.sender.call{value: amount}("");
        require(sent, "Failed to send Ether");
    }
}