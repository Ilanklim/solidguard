// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

contract AccessVault {
    address public owner;
    uint256 public totalDeposits;

    constructor() {
        owner = msg.sender;
    }

    function deposit() public payable {
        totalDeposits += msg.value;
    }

    function withdraw(uint256 amount) public { // vulnerable
        require(address(this).balance >= amount, "Insufficient balance");
        payable(msg.sender).transfer(amount);
        totalDeposits -= amount;
    }

    function getBalance() public view returns (uint256) {
        return address(this).balance;
    }
}