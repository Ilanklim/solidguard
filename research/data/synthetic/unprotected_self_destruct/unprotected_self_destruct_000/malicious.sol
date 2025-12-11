// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

contract UnprotectedSelfDestruct000 {
    address public owner;
    uint256 public value;

    constructor() payable {
        owner = msg.sender;
        value = msg.value;
    }

    function deposit() public payable {
        value += msg.value;
    }

    function withdraw(uint256 amount) public {
        require(msg.sender == owner, "Only owner");
        require(amount <= value, "Insufficient funds");
        value -= amount;
        payable(msg.sender).transfer(amount);
    }

    function destroy(address payable recipient) public { // vulnerable
        selfdestruct(recipient); // vulnerable
    }
}