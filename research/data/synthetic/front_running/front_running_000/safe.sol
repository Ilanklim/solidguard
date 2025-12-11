// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

contract FrontRunningAuctionSafe {
    address public owner;
    uint256 public highestBid;
    address public highestBidder;
    uint256 public auctionEndTime;
    mapping(address => uint256) public pendingReturns;

    constructor(uint256 biddingTime) {
        owner = msg.sender;
        auctionEndTime = block.timestamp + biddingTime;
    }

    function placeBid(uint256 bidAmount) external payable {
        require(block.timestamp < auctionEndTime, "Auction ended");
        require(msg.value == bidAmount, "Sent value must match bid amount");
        require(bidAmount > highestBid, "There already is a higher or equal bid");
        // Prevent sniping: enforce minimum time after each bid
        if (auctionEndTime - block.timestamp < 300) {
            auctionEndTime += 300;
        }

        if (highestBid != 0) {
            pendingReturns[highestBidder] += highestBid;
        }
        highestBid = bidAmount;
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