// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

contract DenialOfService000 {
    address public owner;
    address[] public recipients;
    uint256 public constant MAX_RECIPIENTS = 100;

    constructor() {
        owner = msg.sender;
    }

    function addRecipient(address recipient) public {
        require(msg.sender == owner, "Not owner");
        require(recipients.length < MAX_RECIPIENTS, "Too many recipients");
        recipients.push(recipient);
    }

    function removeRecipient(uint256 index) public {
        require(msg.sender == owner, "Not owner");
        require(index < recipients.length, "Index out of bounds");
        recipients[index] = recipients[recipients.length - 1];
        recipients.pop();
    }

    function distribute() public payable {
        require(msg.value > 0, "No funds sent");
        require(recipients.length > 0, "No recipients");
        require(recipients.length <= MAX_RECIPIENTS, "Recipient cap exceeded");
        uint256 amount = msg.value / recipients.length;
        require(amount > 0, "Amount too small");
        for (uint256 i = 0; i < recipients.length; i++) {
            payable(recipients[i]).transfer(amount);
        }
    }

    function getRecipientCount() public view returns (uint256) {
        return recipients.length;
    }
}