@checkout @R02
Feature: Proceed to checkout
  As a customer
  I want to go from my cart to checkout
  So that I can pay for my order

  # Scope stops at the checkout page: no real payment on the shared demo store.
  @REQ-03 @critical @smoke
  Scenario: Checkout opens from a non-empty cart
    Given the customer has 1 of "Grey jacket" in the cart
    When the customer proceeds to checkout
    Then the checkout page should be shown
    And the checkout should list "Grey jacket"
