Feature:

Background: Valider Background
  Given preparation required

Scenario:
  When A Step is done
  Then A result is processed

Rule:

  Scenario Outline:
    When you make "<this>" happen
    Then "<other>" may be the result

    Examples:
      | this | other |
      | a    | !a    |
      | b    | !b    |
      | c    | !c    |
