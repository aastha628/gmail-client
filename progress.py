import random
import time


class ProgressBar:

    def printProgressBar(self, progress, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
            printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
        """
        val = progress/float(total)
        percent = ("{0:." + str(decimals) + "f}").format(100 * val)
        filledLength = int(length * progress // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
        # Print New Line on Complete
        if progress == total:
            print()

    def start(self):
        print()
        iteration = 0
        while iteration < 100:
            self.printProgressBar(iteration, 100, 'progress',
                                  'complete', 1, 50, printEnd="\r")
            time.sleep(0.2)
            iteration += random.randint(1, 10)

    def end(self):
        self.printProgressBar(100, 100, 'progress',
                              'complete', 1, 50, printEnd="\n")
