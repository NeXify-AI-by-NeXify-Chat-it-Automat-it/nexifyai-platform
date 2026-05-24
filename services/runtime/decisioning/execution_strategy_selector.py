#!/usr/bin/env python3
"""execution_strategy_selector.py"""
import json,logging
log=logging.getLogger("strategy-select")
STRATS={"safe":{"mode":"sequential","verify":"each_step","rollback":"immediate"},"fast":{"mode":"parallel","verify":"end","rollback":"manual"},"governed":{"mode":"sequential","verify":"governance","rollback":"auto"}}
class StrategySelector:
    def select(self,decision):
        risk=decision.get("risk",0.5);critical=decision.get("critical",False)
        if critical or risk>0.7:return STRATS["governed"]
        if risk>0.3:return STRATS["safe"]
        return STRATS["fast"]
SELECTOR=StrategySelector()
