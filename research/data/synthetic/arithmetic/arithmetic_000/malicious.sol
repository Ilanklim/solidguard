// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

contract ArithmeticVuln {
    mapping(address => uint256) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw(uint256 amount) public {
        require(amount > 0, "Amount zero");
        balances[msg.sender] -= amount; // vulnerable
        (bool sent, ) = msg.sender.call{value: amount}("");
        require(sent, "Failed to send Ether");
    }

    function checkBalance(address user) public view returns (uint256) {
        return balances[user];
    }
}