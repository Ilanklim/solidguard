// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

contract UserSecretStorage {
    // No storage of unencrypted private data
    // Only hashes are stored for verification
    mapping(address => bytes32) private userSecretHashes;

    function storeSecret(bytes32 secretHash) public {
        userSecretHashes[msg.sender] = secretHash;
    }

    function verifySecret(string memory secret) public view returns (bool) {
        return keccak256(abi.encodePacked(secret)) == userSecretHashes[msg.sender];
    }
}