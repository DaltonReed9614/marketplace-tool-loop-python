import json

from src.marketplace_agent import BuyerUpdate, SellerAsset, handoff_order


def main() -> None:
    asset = SellerAsset(sku="mug-42", title="Stoneware mug", quantity=3)
    update = BuyerUpdate(buyer_id="buyer-7", sku="mug-42", quantity=2)
    print(json.dumps(handoff_order(asset, update).__dict__, indent=2))


if __name__ == "__main__":
    main()
