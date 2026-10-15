from src.marketplace_agent import BuyerUpdate, SellerAsset, handoff_order


def test_handoff_requires_enough_inventory() -> None:
    asset = SellerAsset("mug-42", "Stoneware mug", 1)
    update = BuyerUpdate("buyer-7", "mug-42", 2)
    assert handoff_order(asset, update).status == "needs_review"


def test_handoff_marks_fulfillable_update_ready() -> None:
    asset = SellerAsset("mug-42", "Stoneware mug", 3)
    update = BuyerUpdate("buyer-7", "mug-42", 2)
    assert handoff_order(asset, update).status == "ready_for_handoff"
