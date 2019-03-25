import json


class ValidationEngine:
    def __init__(self, rule_engine, process_results):
        self.processResults = process_results
        self.ruleEngine = rule_engine
        self._report = {}

    def validate(self):
        """ Grabs the next validation rule and calls the function with the arguments """
        current_rule = self.ruleEngine.next_rule()
        if current_rule:
            current_rule_name = current_rule.get_rule_type()
            print('Working on: ' + current_rule_name)
            current_rule.set_results(self.processResults)

            self._report[current_rule_name] = current_rule.apply()
            print('Result of rule: ' + str(current_rule.has_passed()))
            self.validate()
        else:
            print('Validation done, results are in!')
            with open('ValidationReport.json', 'w') as fp:
                json.dump(self._report, fp)


