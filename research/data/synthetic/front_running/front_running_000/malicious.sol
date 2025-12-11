// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

contract FrontRunningAuction {
    address public owner;
    uint256 public highestBid;
    address public highestBidder;
    uint256 public auctionEndTime;
    mapping(address => uint256) public pendingReturns;

    constructor(uint256 biddingTime) {
        owner = msg.sender;
        auctionEndTime = block.timestamp + biddingTime;
    }

    function placeBid() external payable {
        require(block.timestamp < auctionEndTime, "Auction ended");
        require(msg.value > highestBid, "There already is a higher or equal bid");
        
        if (highestBid != 0) {
            pendingReturns[highestBidder] += highestBid;
        }
        highestBid = msg.value; // vulnerable
        highestBidder = msg.sender;
    }

    function withdraw() external {
        uint256 amount = pendingReturns[msg.sender];
        require(amount > 0, "Nothing to withdraw");
        pendingReturns[msg.sender] = 0;
        (bool sent, ) = payable(msg.sender).call{value: amount}("");
        require(sent, "Failed to send Ether");
    }

    function endAuction() external {
        require(msg.sender == owner, "Only owner can end auction");
        require(block.timestamp >= auctionEndTime, "Auction still ongoing");
        payable(owner).transfer(highestBid);
        highestBid = 0;
    }
}