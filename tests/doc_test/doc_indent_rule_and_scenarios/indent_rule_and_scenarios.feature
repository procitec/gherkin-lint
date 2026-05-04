Feature: Das ist ein valides Feature

Background: Valider Background
  Given preparation required

Scenario: Valides Scenario
  When A Step is done
  Then A result is processed

Rule: After this role no mor scenarios allowed

  Scenario: Ok
    Given a precondtion
    Then we are ready

Scenario: No Scenario after Rule
  Given a precondition
  Then we are ready
