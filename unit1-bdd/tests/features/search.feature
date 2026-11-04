@search @R07 @medium
Feature: Product search
  As a customer
  I want to find products by keyword
  So that I do not have to browse the whole catalog

  @REQ-08 @regression
  Scenario: Search returns matching products
    Given the customer is on the home page
    When the customer searches for "jacket"
    Then the results should include "Grey jacket"
    And the results should include "Noir jacket"

  @REQ-08 @negative @regression
  Scenario: Search with no matching products
    Given the customer is on the home page
    When the customer searches for "zzqxnotaproduct"
    Then no products should be shown in the results
