@register @R06 @medium
Feature: Customer registration
  As a new customer
  I want to create an account
  So that I can log in next time

  @negative @regression
  Scenario: Registration is rejected without an email
    Given the customer is on the registration page
    When the customer registers without an email address
    Then a registration error should be shown

  # Creates a real account on the shared store: excluded by default (see behave.ini).
  @data-creating
  Scenario: Registration succeeds with valid details
    Given the customer is on the registration page
    When the customer registers with a new random email
    Then the customer should be logged in
