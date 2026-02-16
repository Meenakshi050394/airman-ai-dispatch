# Dispatch Rules Document
# ============================================

## RULE_DISPATCH_001
Weather_Category: VMC
Sortie_Type: ANY
Action: PROCEED
Description: In visual meteorological conditions, all flights may proceed as planned.

## RULE_DISPATCH_002
Weather_Category: MVFR
Sortie_Type: ANY
Action: CAUTION_PROCEED
Description: In marginal VFR conditions, flights may proceed with caution.

## RULE_DISPATCH_003
Weather_Category: IMC
Sortie_Type: C172
Action: CONVERT_TO_SIM
Description: In IMC conditions, C172 sorties must be converted to simulator sessions.

## RULE_DISPATCH_004
Weather_Category: IMC
Sortie_Type: DA42
Action: IFR_ALLOWED
Description: DA42 aircraft may proceed under instrument flight rules.

## RULE_DISPATCH_005
Weather_Category: LIFR
Sortie_Type: ANY
Action: CANCEL
Description: In low instrument conditions, all sorties must be cancelled.
