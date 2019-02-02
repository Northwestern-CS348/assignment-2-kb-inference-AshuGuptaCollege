import read, copy
from util import *
from logical_classes import *

verbose = 0

class KnowledgeBase(object):
    def __init__(self, facts=[], rules=[]):
        self.facts = facts
        self.rules = rules
        self.ie = InferenceEngine()

    def __repr__(self):
        return 'KnowledgeBase({!r}, {!r})'.format(self.facts, self.rules)

    def __str__(self):
        string = "Knowledge Base: \n"
        string += "\n".join((str(fact) for fact in self.facts)) + "\n"
        string += "\n".join((str(rule) for rule in self.rules))
        return string

    def _get_fact(self, fact):
        """INTERNAL USE ONLY
        Get the fact in the KB that is the same as the fact argument

        Args:
            fact (Fact): Fact we're searching for

        Returns:
            Fact: matching fact
        """
        for kbfact in self.facts:
            if fact == kbfact:
                return kbfact

    def _get_rule(self, rule):
        """INTERNAL USE ONLY
        Get the rule in the KB that is the same as the rule argument

        Args:
            rule (Rule): Rule we're searching for

        Returns:
            Rule: matching rule
        """
        for kbrule in self.rules:
            if rule == kbrule:
                return kbrule

    def kb_add(self, fact_rule):
        """Add a fact or rule to the KB
        Args:
            fact_rule (Fact|Rule) - the fact or rule to be added
        Returns:
            None
        """
        printv("Adding {!r}", 1, verbose, [fact_rule])
        if isinstance(fact_rule, Fact):
            if fact_rule not in self.facts:
                self.facts.append(fact_rule)
                for rule in self.rules:
                    self.ie.fc_infer(fact_rule, rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.facts.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.facts[ind].supported_by.append(f)
                else:
                    ind = self.facts.index(fact_rule)
                    self.facts[ind].asserted = True
        elif isinstance(fact_rule, Rule):
            if fact_rule not in self.rules:
                self.rules.append(fact_rule)
                for fact in self.facts:
                    self.ie.fc_infer(fact, fact_rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.rules.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.rules[ind].supported_by.append(f)
                else:
                    ind = self.rules.index(fact_rule)
                    self.rules[ind].asserted = True

    def kb_assert(self, fact_rule):
        """Assert a fact or rule into the KB

        Args:
            fact_rule (Fact or Rule): Fact or Rule we're asserting
        """
        printv("Asserting {!r}", 0, verbose, [fact_rule])
        self.kb_add(fact_rule)

    def kb_ask(self, fact):
        """Ask if a fact is in the KB

        Args:
            fact (Fact) - Statement to be asked (will be converted into a Fact)

        Returns:
            listof Bindings|False - list of Bindings if result found, False otherwise
        """
        print("Asking {!r}".format(fact))
        if factq(fact):
            f = Fact(fact.statement)
            bindings_lst = ListOfBindings()
            # ask matched facts
            for fact in self.facts:
                binding = match(f.statement, fact.statement)
                if binding:
                    bindings_lst.add_bindings(binding, [fact])

            return bindings_lst if bindings_lst.list_of_bindings else []

        else:
            print("Invalid ask:", fact.statement)
            return []

    def kb_retract(self, fact_or_rule):
        """Retract a fact from the KB

        Args:
            fact (Fact) - Fact to be retracted

        Returns:
            None
        """
        printv("Retracting {!r}", 0, verbose, [fact_or_rule])
        ####################################################
        # Student code goes here
        if isinstance(fact_or_rule, Fact):
            for my_fact in self.facts:
                if my_fact.statement == fact_or_rule.statement:
                    self.retract_helper(my_fact)


    def retract_helper(self, fact_or_rule):
        if isinstance(fact_or_rule, Rule):
            if fact_or_rule.supported_by == []:
                for rule in fact_or_rule.supports_rules:
                    # we remove object from the supported_by list of all rules it supports
                    for couple in rule.supported_by:
                        if couple[1] == fact_or_rule:
                            rule.supported_by.remove(couple)
                    # we retract the rule if its not supported by anything else other than this
                    if rule.supported_by == []:
                        self.retract_helper(rule)

                for my_fact in fact_or_rule.supports_facts:
                    # we remove the object from the supported_by list of all facts it supports
                    for couple in my_fact.supported_by:
                        if couple[1] == fact_or_rule:
                            my_fact.supported_by.remove(couple)
                    # we retract the fact if its not supported by anything else other than this
                    if my_fact.supported_by == []:
                        self.retract_helper(my_fact)
                self.rules.remove(fact_or_rule)

            elif len(fact_or_rule.supported_by) > 0:
                fact_or_rule.asserted = False
        # most of this part is the same as above
        elif isinstance(fact_or_rule, Fact):
            if fact_or_rule.supported_by == []:
                for my_rule in fact_or_rule.supports_rules:
                    for couple in my_rule.supported_by:
                        if couple[0] == fact_or_rule:
                            my_rule.supported_by.remove(couple)
                    if my_rule.supported_by == []:
                        self.retract_helper(my_rule)

                for my_fact in fact_or_rule.supports_facts:
                    for couple in my_fact.supported_by:
                        if couple[0] == fact_or_rule:
                            my_fact.supported_by.remove(couple)
                    if my_fact.supported_by == []:
                        self.retract_helper(my_fact)
                self.facts.remove(fact_or_rule)

            elif len(fact_or_rule.supported_by) > 0:
                fact_or_rule.asserted = False


class InferenceEngine(object):
    def fc_infer(self, fact, rule, kb):
        """Forward-chaining to infer new facts and rules

        Args:
            fact (Fact) - A fact from the KnowledgeBase
            rule (Rule) - A rule from the KnowledgeBase
            kb (KnowledgeBase) - A KnowledgeBase

        Returns:
            Nothing            
        """
        printv('Attempting to infer from {!r} and {!r} => {!r}', 1, verbose,
            [fact.statement, rule.lhs, rule.rhs])
        ####################################################
        # Student code goes here
        first_element = rule.lhs[0]
        my_bindings = match(fact.statement, first_element)
        if my_bindings is not False:
            # we have more than one element on the left hand side of the rule
            if len(rule.lhs) > 1:
                # we need to look at the rest of the elements on the lhs
                lhs_popped = rule.lhs[:]
                # ...so pop the first element
                lhs_popped.pop(0)
                # instantiate rhs of rule with bindings
                right_side = instantiate(rule.rhs, my_bindings)
                # instantiate remaining elements with bindings
                left_side = [instantiate(element, my_bindings) for element in lhs_popped]
                supported_by_list = [[fact, rule]]
                rule_to_add = Rule([left_side, right_side], supported_by_list)
                kb.kb_add(rule_to_add)
                fact.supports_rules.append(rule_to_add)
                rule.supports_rules.append(rule_to_add)
            # there's only one part to the left hand side of the rule
            elif len(rule.lhs) == 1:
                new_statement = instantiate(rule.rhs, my_bindings)
                # we can assert a new fact
                supported_by_list = [[fact, rule]]
                fact_to_add = Fact(new_statement, supported_by_list)
                kb.kb_add(fact_to_add)
                # add this new fact to the supports list of fact and rule
                fact.supports_facts.append(fact_to_add)
                rule.supports_facts.append(fact_to_add)