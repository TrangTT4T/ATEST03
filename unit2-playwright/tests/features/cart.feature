@cart
Feature: Shopping cart
  As a customer
  I want to manage products in my cart
  So that I can buy what I need

  @critical @smoke
  Scenario: Add an in-stock product to the cart
    Given the customer is viewing the product "Grey jacket"
    When the customer adds the product to the cart
    Then the cart should contain 1 item
    And the cart total should be "£55.00"

  @critical @regression
  Scenario Outline: Cart total equals price times quantity
    Given the customer has <quantity> of "<product>" in the cart
    When the customer opens the cart
    Then the cart should contain <quantity> items
    And the cart total should be "<total>"

    Examples:
      | product     | quantity | total   |
      | Noir jacket | 2        | £120.00 |
      | Striped top | 3        | £150.00 |

  @critical @regression
  Scenario: Change the quantity of a product in the cart
    Given the customer has 1 of "Bronze sandals" in the cart
    When the customer changes the quantity of "Bronze sandals" to 2
    Then the cart should contain 2 items
    And the cart total should be "£79.98"

  @critical @regression
  Scenario: Remove the only product from the cart
    Given the customer has 1 of "Striped top" in the cart
    When the customer removes "Striped top" from the cart
    Then the cart should be empty
