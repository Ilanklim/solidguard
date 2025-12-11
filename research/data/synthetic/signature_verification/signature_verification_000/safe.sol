// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

contract SignatureVerifierSafe {
    address public owner;
    mapping(address => uint256) public nonces;

    event Claimed(address indexed user, uint256 amount);

    constructor() {
        owner = msg.sender;
    }

    function claim(uint256 amount, uint8 v, bytes32 r, bytes32 s) external {
        bytes32 message = keccak256(
            abi.encodePacked(address(this), block.chainid, msg.sender, amount, nonces[msg.sender])
        );
        address signer = ecrecover(toEthSignedMessageHash(message), v, r, s);
        require(signer == owner, "Invalid signature");

        nonces[msg.sender]++;
        payable(msg.sender).transfer(amount);
        emit Claimed(msg.sender, amount);
    }

    function deposit() external payable {}

    function toEthSignedMessageHash(bytes32 hash) internal pure returns (bytes32) {
        return keccak256(abi.encodePacked("\x19Ethereum Signed Message:\n32", hash));
    }

    function getNonce(address user) external view returns (uint256) {
        return nonces[user];
    }
}