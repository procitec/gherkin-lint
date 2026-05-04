Feature: No empty given

Background:
  Given a single precondition

Scenario: A context
  Given an standalone given

Scenario Outline: an text
  Given an outline given
  When ok step
  Then ok then

  Examples:
    |a|b|
    |s|d|
