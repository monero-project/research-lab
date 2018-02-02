import unittest, random, time

class StochasticProcess(object):
    ''' 
    Stochastic processes have a clock and a state.
    The clock moves forward, and then the state updates.
    More detail requires knowledge of the underlying stochProc.
    '''
    def __init__(self, params=None):
        # initialize with initial data
        self.data = params
        self.t = 0.0 # should always start at t=0.0
        self.state = 0.0 # magic number
        self.maxTime = 1000.0 # magic number
        self.saveFile = "output.csv"
        self.verbose = True
        
    def go(self):
        # Executes stochastic process.
        assert self.maxTime > 0.0 # Check loop will eventually terminate.
        t = self.t
        while t <= self.maxTime: 
            deltaT = self.getNextTime() # Pick the next "time until event" and a description of the event.
            self.updateState(t, deltaT) # Update state with deltaT input
            t = self.t
            if self.verbose:
                print("Recording...")
            self.record()
            
    def getNextTime(self):
        return 1 # Magic number right now
        
    def updateState(self, t, deltaT):
        # Update the state of the system. In this case,
        # we are doing a random walk on the integers.
        self.state += random.randrange(-1,2,1) # [-1, 0, 1]
        self.t += deltaT
        
    def record(self):
        with open(self.saveFile,"w") as recordKeeper:
            line = str(self.t) + ",\t" + str(self.state) + "\n"
            recordKeeper.write(line)
    
class Test_StochasticProcess(unittest.TestCase):
    def test_sp(self):
        sally = StochasticProcess()
        sally.verbose = False
        sally.go()
        
suite = unittest.TestLoader().loadTestsFromTestCase(Test_StochasticProcess)
unittest.TextTestRunner(verbosity=1).run(suite)


