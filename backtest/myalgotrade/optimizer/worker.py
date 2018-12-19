import cPickle as pickle
import multiprocessing
import socket
import xmlrpclib
import time

import pyalgotrade
from pyalgotrade.barfeed import OptimizerBarFeed
import pyalgotrade.logger
from pyalgotrade.optimizer.worker import call_and_retry_on_network_error

from myalgotrade import strategy
import jobutil


class Worker(object):
    def __init__(self, address, port, worker_name=None):
        url = "http://%s:%s%s" % (address, port, jobutil.RPC_PATH)
        self.__server = xmlrpclib.ServerProxy(url, allow_none=True)
        self.__logger = pyalgotrade.logger.getLogger(worker_name)
        if worker_name is None:
            self.worker_name = socket.gethostname()
        else:
            self.worker_name = worker_name

        self.job_config = None

    def get_job_configs(self):
        configs = call_and_retry_on_network_error(self.__server.get_job_configs, 3)
        # configs = jobutil.JobConfigs
        configs = pickle.loads(configs)
        return configs

    def get_next_job(self):
        job = call_and_retry_on_network_error(self.__server.get_next_job, 3)
        # job = jobutil.Job
        job = pickle.loads(job)
        return job

    def _process_job(self, job):
        best_result = None
        parameters = job.getNextParameters()
        best_params = parameters

        print 'process job:', self.job_config.bars_dict.keys()
        while parameters is not None:
            feeds = {}
            for name in self.job_config.bars_dict.keys():
                # Wrap the bars into a feed.
                feeds[name] = OptimizerBarFeed(self.job_config.frequency_dict[name], self.job_config.instruments_dict[name],
                                               self.job_config.bars_dict[name])
            # Run the strategy.
            self.get_logger().info("Running strategy with parameters %s" % (str(parameters)))
            result = strategy.run_strategy(self.job_config.strategy_class, feeds, self.job_config.log_key, parameters)
            self.get_logger().info("Result %s" % result)
            self.get_logger().info(','.join(str(s) for s in (job.getId(), result, parameters)))

            if best_result is None or self.job_config.result_comparator.compare(result, best_result):
                best_result = result
                best_params = parameters
            # Run with the next set of parameters.
            parameters = job.getNextParameters()

        assert (best_params is not None)
        self.push_job_results(job.getId(), best_result, best_params)

    def get_logger(self):
        return self.__logger

    def push_job_results(self, job_id, result, parameters):
        job_id = pickle.dumps(job_id)
        result = pickle.dumps(result)
        parameters = pickle.dumps(parameters)
        worker_name = pickle.dumps(self.worker_name)
        call_and_retry_on_network_error(self.__server.push_job_results, 3, job_id, result, parameters, worker_name)

    def run(self):
        # Get the instruments and bars, and other configs.
        self.job_config = self.get_job_configs()

        # Process jobs
        job = self.get_next_job()
        while job is not None:
            self._process_job(job)
            job = self.get_next_job()


def worker_process(address, port, workerName):
    # Create a worker and run it.
    w = Worker(address, port, workerName)
    # cProfile.runctx('w.run()', globals(), locals(), workerName + '.profile')
    w.run()


def run(address, port, workerCount=None, workerName=None):
    """Executes one or more worker processes that will run a strategy with the bars and parameters supplied by the server.

    :param strategyClass: The strategy class.
    :param address: The address of the server.
    :type address: string.
    :param port: The port where the server is listening for incoming connections.
    :type port: int.
    :param workerCount: The number of worker processes to run. If None then as many workers as CPUs are used.
    :type workerCount: int.
    :param workerName: A name for the worker. A name that identifies the worker. If None, the hostname is used.
    :type workerName: string.
    """

    assert (workerCount is None or workerCount > 0)
    if workerCount is None:
        workerCount = multiprocessing.cpu_count()

    print 'starting workers on port:', port
    print 'worker num:', workerCount

    workers = []
    # Build the worker processes.
    for i in range(workerCount):
        workers.append(
                multiprocessing.Process(target=worker_process,
                                        args=(address, port, workerName + str(i))))

    # Start workers
    for process in workers:
        process.start()

    # Wait workers
    for process in workers:
        process.join()


def run_workers_forever(port):
    while (1):
        time.sleep(2)
        run('localhost', port, multiprocessing.cpu_count(), 'local')


def main():
    process_all = []
    from myalgotrade.optimizer import jobutil
    dt_port = jobutil.port_dict['dt']
    process_dt = multiprocessing.Process(target=run_workers_forever, args=(dt_port,))
    process_all.append(process_dt)

    # ab_port = jobutil.port_dict['ab']
    # process_ab = multiprocessing.Process(target=run_workers_forever, args=(ab_port,))
    # process_all.append(process_ab)

    for process in process_all:
        process.start()

    for process in process_all:
        process.join()


if __name__ == '__main__':
    main()
