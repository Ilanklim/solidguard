// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

contract InitializationMaliciousSafe {
    address public owner;
    bool public initialized;

    function initialize() public {
        require(!initialized, "Already initialized");
        owner = msg.sender;
        initialized = true;
    }

    function privilegedFunction() external view returns (string memory) {
        require(msg.sender == owner, "Not owner");
        return "Sensitive Data";
    }
}