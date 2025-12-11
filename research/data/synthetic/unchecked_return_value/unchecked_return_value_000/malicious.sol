// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

contract PaymentProcessorUnchecked {
    address public owner;
    address public trustedRecipient;

    event PaymentSent(address indexed from, address indexed to, uint256 amount, bytes data);

    constructor(address _trustedRecipient) {
        owner = msg.sender;
        trustedRecipient = _trustedRecipient;
    }

    function setRecipient(address _recipient) external {
        require(msg.sender == owner, "Only owner can set recipient");
        trustedRecipient = _recipient;
    }

    function sendPayment(uint256 amount, bytes calldata data) external {
        require(amount > 0, "Amount must be positive");
        require(address(this).balance >= amount, "Insufficient contract balance");
        // vulnerable
        trustedRecipient.call{value: amount}(data);
        emit PaymentSent(msg.sender, trustedRecipient, amount, data);
    }

    receive() external payable {}
}