Feature: Das ist ein valides Feature


Background: Valider Background
  Given preparation required
  * do this too

Scenario: Valides Scenario
  When A Step is done
  * A Step is done too

  When another step is done

  Then A result is processed
  * another step is called

  Then another result is processed

Scenario: not valid
  When A Step is done
  * A Step is done too
  When another step is done
  Then A result is processed
  * another step is called
  Then another result is processed
