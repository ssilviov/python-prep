from typing import Callable
import threading

class H2O:
    """Leetcode 1117"""
   def __init__(self):
       self.oxygen_s = threading.Semaphore(1)
       self.hydrogen_s = threading.Semaphore(2)
       self.mutex = threading.Lock()
       self.h_count = 0


   def hydrogen(self, releaseHydrogen: 'Callable[[], None]') -> None:
       self.hydrogen_s.acquire()

       # releaseHydrogen() outputs "H". Do not change or remove this line.
       releaseHydrogen()

       with self.mutex:
           self.h_count += 1
           if self.h_count == 2:
               self.h_count = 1
               self.oxygen_s.release()


   def oxygen(self, releaseOxygen: 'Callable[[], None]') -> None:
       
       self.oxygen_s.acquire()
       # releaseOxygen() outputs "O". Do not change or remove this line.
       releaseOxygen()

       self.hydrogen_s.release()
       self.hydrogen_s.release()


class PrintinOrder:
    """Leet code 114."""
    def __init__(self):
        self.second_sem = threading.Semaphore(0)
        self.third_sem = threading.Semaphore(0)


    def first(self, printFirst: 'Callable[[], None]') -> None:
        
        # printFirst() outputs "first". Do not change or remove this line.
        printFirst()
        self.second_sem.release()


    def second(self, printSecond: 'Callable[[], None]') -> None:
        self.second_sem.acquire()
        
        # printSecond() outputs "second". Do not change or remove this line.
        printSecond()
        self.third_sem.release()


    def third(self, printThird: 'Callable[[], None]') -> None:
        
        self.third_sem.acquire()
        # printThird() outputs "third". Do not change or remove this line.
        printThird()


class FizzBuzz:
    """Leetcode 1195."""
    def __init__(self, n: int):
        self.n = n
        self.i = 1
        self.fizz_s = threading.Semaphore(0)
        self.buzz_s = threading.Semaphore(0)
        self.fizzbuzz_s = threading.Semaphore(0)
        self.number_s = threading.Semaphore(1)

        # n is always greater or equal 1 so number can always run first.

    def unblock_next(self):
        if self.i % 3 == 0 and self.i % 5 == 0:
            self.fizzbuzz_s.release()
            return

        if self.i % 3 == 0: 
            self.fizz_s.release()
            return

        if self.i % 5 == 0: 
            self.buzz_s.release()
            return

        self.number_s.release()

    # printFizz() outputs "fizz"
    def fizz(self, printFizz: 'Callable[[], None]') -> None:
        while True:
            self.fizz_s.acquire()
            printFixx()
            self.i +=1
            self.unblock_next()
    	

    # printBuzz() outputs "buzz"
    def buzz(self, printBuzz: 'Callable[[], None]') -> None:
        while True:
            self.buzz_s.acquire()
            printBuzz()
            self.i +=1
            self.unblock_next()
    	

    # printFizzBuzz() outputs "fizzbuzz"
    def fizzbuzz(self, printFizzBuzz: 'Callable[[], None]') -> None:
        while True:
            self.fizzbuzz_s.acquire()
            printFizzBuzz()
            self.i +=1
            self.unblock_next()
        

    # printNumber(x) outputs "x", where x is an integer.
    def number(self, printNumber: 'Callable[[int], None]') -> None:
        while True:
            self.fizz_s.acquire()
            self.number_s.acquire()
            printNumber(self.i)
            self.i +=1
            self.unblock_next()


class DiningPhilosophers:
    """Leetcode 1126."""

    def __init__(self):
        self.forks = [threading.Semaphore(1) for i in range(5)]

    def pickOrder(self, philosopher):
        if i == 0:
            return [0, 4]
        return [i, i+1]


    # call the functions directly to execute, for example, eat()
    def wantsToEat(self,
                   philosopher: int,
                   pickLeftFork: 'Callable[[], None]',
                   pickRightFork: 'Callable[[], None]',
                   eat: 'Callable[[], None]',
                   putLeftFork: 'Callable[[], None]',
                   putRightFork: 'Callable[[], None]') -> None:

        left = philosopher
        right = (philosopher + 1) % 5

        if philosopher % 2 == 0:
            self.forks[left].acquire()
            self.forks[right].acquire()
        else:
            self.forks[right].acquire()
            self.forks[left].acquire()
    
        pickLeftFork()
        pickRightFork()
        eat()
        putLeftFork()
        putRightFork()

        if philosopher % 2 == 0:
            self.forks[right].acquire()
            self.forks[left].acquire()
        else:
            self.forks[left].acquire()
            self.forks[right].acquire()



