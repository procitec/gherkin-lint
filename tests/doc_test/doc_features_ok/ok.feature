Feature: Das ist ein valides Feature

Was immer das Tut, es tut was es tut
das kann viel sein oder auch nicht

Background: Valider Background

  Der bereitet alles mal so vor

  Given preparation required

Scenario: Valides Scenario

  Das ist auch möglich
  auch mehrzeilig

  When A Step is done
  Then A result is processed

# use star instead and
Scenario: Valides Scenario

  einzeilig geht auch

  When A Step is done
  * a second step is done
  Then A result is processed

@tbc
Scenario: Very long
  When We do something
  Then this may last

  When we repeat it
  Then is may last longer

  When we do not repeat it
  * we repeat it
  Then it may be sooooo much longer

Rule: This is a rule

  Ebenso bei rules

  Background: This i scenario
    Given you are suprised

  @wip
  Scenario: after suprised
    When I look at you
    Then you grin
