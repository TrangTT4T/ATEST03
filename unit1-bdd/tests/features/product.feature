@product
Feature: Product information
  As a customer
  I want correct product names, prices and stock status
  So that I know what I am buying

  @REQ-06 @R05 @high @regression
  Scenario Outline: Catalog shows correct price and stock status
    When the customer browses the full catalog
    Then the product "<product>" should be listed at its catalog price
    And the product "<product>" should be shown as "<status>"

    Examples:
      | product        | status    |
      | Black heels    | available |
      | Bronze sandals | available |
      | Brown Shades   | sold out  |
      | Grey jacket    | available |
      | Noir jacket    | available |
      | Striped top    | available |
      | White sandals  | sold out  |

  @REQ-04 @R03 @high @regression
  Scenario: Product page shows the catalog name and price
    Given the customer is viewing the product "Noir jacket"
    Then the product page should show the name "Noir jacket"
    And the product page should show the price "£60.00"

  @REQ-04 @R03 @high @negative @regression
  Scenario: A sold-out product cannot be added to the cart
    Given the customer is viewing the product "Brown Shades"
    Then the customer should not be able to add it to the cart
