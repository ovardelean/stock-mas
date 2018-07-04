import sys
from agents.feeder.agent import Feeder
from agents.predictor.agent import Predictor
from agents.evaluator.agent import Evaluator


def main():
    if sys.argv[1] == 'feeder':
        print "Running Feeder.."
        feeder = Feeder()
        feeder.run()
    elif sys.argv[1] == 'predictor':
        print "Running Predictor.."
        predictor = Predictor()
        predictor.run()
    elif sys.argv[1] == 'evaluator':
        print "Running Evaluator.."
        evaluator = Evaluator()
        evaluator.run()

if __name__ == "__main__":
    main()