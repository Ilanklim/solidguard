// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

contract UserSecretStorage {
    // Private user secrets stored in plaintext (vulnerability)
    mapping(address => string) private userSecrets; // vulnerable

    function storeSecret(string memory secret) public {
        userSecrets[msg.sender] = secret;
    }

    function getMySecret() public view returns (string memory) {
        return userSecrets[msg.sender];
    }
}