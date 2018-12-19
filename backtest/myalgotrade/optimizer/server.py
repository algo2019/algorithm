import cPickle as pickle
import SimpleXMLRPCServer
import threading
import pyalgotrade.logger
import time
import datetime

import jobutil

class AutoStopThread(threading.Thread):
    def __init__(self, server):
        threading.Thread.__init__(self)
        self.__server = server

    def run(self):
        while self.__server.jobs_pending():
            time.sleep(1)
        self.__server.stop()


class RequestHandler(SimpleXMLRPCServer.SimpleXMLRPCRequestHandler):
    rpc_paths = (jobutil.RPC_PATH,)


class Server(SimpleXMLRPCServer.SimpleXMLRPCServer):
    def __init__(self, address, port, batch_size=jobutil.DEFAULT_BATCH_SIZE, auto_stop=True):
        SimpleXMLRPCServer.SimpleXMLRPCServer.__init__(self, (address, port), requestHandler=RequestHandler,
                                                       logRequests=False, allow_none=True)
        self.batch_size = batch_size

        self.strategy_class = None
        self.result_comparator = None
        self.log_key = None
        self.bars_dict = None
        self.frequency_dict = None
        self.instruments_dict = None

        self.active_jobs = {}
        self.best_job = None

        self.__active_jobs_lock = threading.Lock()
        self.__parameters_lock = threading.Lock()
        self.__parameters_iterator = None
        self.__logger = pyalgotrade.logger.getLogger("server")
        if auto_stop:
            self.__auto_stop_thread = AutoStopThread(self)
        else:
            self.__auto_stop_thread = None

        self.register_introspection_functions()
        self.register_function(self.get_job_configs, 'get_job_configs')
        self.register_function(self.get_next_job, 'get_next_job')
        self.register_function(self.push_job_results, 'push_job_results')
        self.__forced_stop = False
        self.total_jobs = 0

    def _get_next_params(self):
        ret = []
        # Get the next set of parameters.
        with self.__parameters_lock:
            if self.__parameters_iterator is not None:
                try:
                    for i in xrange(self.batch_size):
                        ret.append(self.__parameters_iterator.next())
                except StopIteration:
                    self.__parameters_iterator = None
        return ret

    def get_logger(self):
        return self.__logger

    def get_best_job(self):
        return self.best_job

    def get_next_job(self):
        ret = None
        # Get the next set of parameters.
        params = self._get_next_params()

        # Map the active job
        if len(params):
            ret = jobutil.Job(params)
            with self.__active_jobs_lock:
                self.active_jobs[ret.getId()] = ret

            self.total_jobs += len(params)
            self.get_logger().info('pushing jobs, total %d' % self.total_jobs)
        return pickle.dumps(ret)

    def jobs_pending(self):
        if self.__forced_stop:
            return False

        with self.__parameters_lock:
            is_jobs_pending = self.__parameters_iterator is not None
        with self.__active_jobs_lock:
            is_active_jobs = len(self.active_jobs) > 0
        return is_jobs_pending or is_active_jobs

    def stop(self):
        self.shutdown()

    def push_job_results(self, job_id, result, parameters, worker_name):
        job_id = pickle.loads(job_id)
        result = pickle.loads(result)
        parameters = pickle.loads(parameters)
        worker_name = pickle.loads(worker_name)

        job = None

        # Get the active job and remove the mapping.
        with self.__active_jobs_lock:
            try:
                job = self.active_jobs[job_id]
                del self.active_jobs[job_id]
            except KeyError:
                # The job's results were already submitted.
                return

        # Save the job with the best result
        if self.best_job is None or self.result_comparator.compare(result, self.best_job.getBestResult()):
            job.setBestResult(result, parameters, worker_name)
            self.best_job = job

        self.get_logger().info("Partial result %s with parameters: %s from %s" % (result, parameters, worker_name))

    def get_job_configs(self):
        self.get_logger().info('pushing job configs')
        configs = jobutil.JobConfigs(self.strategy_class, self.instruments_dict, self.bars_dict, self.frequency_dict, self.log_key,
                                     self.result_comparator)
        return pickle.dumps(configs)

    def serve(self, strategy_class=None, bar_feed_dict=None, parameter_set=None, log_key=None, result_comparator=None):
        for arg in (strategy_class, bar_feed_dict, result_comparator, log_key, parameter_set):
            if arg is None:
                print 'args:', (strategy_class, bar_feed_dict, result_comparator, log_key, parameter_set)
                raise Exception('args all required!')

        self.strategy_class = strategy_class
        self.result_comparator = result_comparator
        self.log_key = log_key
        ret = None
        self.total_jobs = 0
        try:
            # Initialize instruments, bars and parameters.
            self.get_logger().info("Loading bars")
            self.instruments_dict = {}
            self.bars_dict = {}
            self.frequency_dict = {}
            for bar_name, bar_feed in bar_feed_dict.items():
                bars_value_list = []
                for datetime_, bars in bar_feed:
                    bars_value_list.append(bars)
                instruments = bar_feed.getRegisteredInstruments()
                self.instruments_dict[bar_name] = instruments
                self.bars_dict[bar_name] = bars_value_list
                self.frequency_dict[bar_name] = bar_feed.getFrequency()

            self.__parameters_iterator = iter(parameter_set)

            if self.__auto_stop_thread:
                self.__auto_stop_thread.start()

            self.get_logger().info("Waiting for workers")
            self.serve_forever()

            if self.__auto_stop_thread:
                self.__auto_stop_thread.join()

            # Show the best result.
            best_job = self.get_best_job()
            if best_job:
                self.get_logger().info("Best final result %s with parameters: %s from client %s" % (
                    best_job.getBestResult(), best_job.getBestParameters(), best_job.getBestWorkerName()))
                ret = jobutil.Results(best_job.getBestParameters(), best_job.getBestResult())
            else:
                self.get_logger().error("No jobs processed")
        finally:
            self.__forced_stop = True
        return ret


def run_server_once(strategy_class, bar_feed_dict, params_set, log_key, result_comparator, port, address='localhost',
                    batch_size=jobutil.DEFAULT_BATCH_SIZE):
    if port is None:
        port = jobutil.find_port_by_default()

    print datetime.datetime.now(), 'server on', port
    print 'strategy:', strategy_class.__module__ + '.' + strategy_class.__name__
    s = Server(address, port, batch_size)
    result = s.serve(strategy_class=strategy_class, bar_feed_dict=bar_feed_dict, parameter_set=params_set,
                     log_key=log_key, result_comparator=result_comparator)
    s.server_close()
    print datetime.datetime.now(), 'server closed on', port
    return result


def test_dt():
    import datetime
    from myalgotrade.strategy import dt_strategy
    from myalgotrade import feed
    from myalgotrade.feed import feed_manager
    csv_infos = {
        'l': (
            '../data/l1509_1min.csv', feed.Frequency.MINUTE, feed.GenericRowParser(frequency=feed.Frequency.MINUTE)),
        # 'ag': (
        #     '../data/test_bar.csv', feed.Frequency.MINUTE, feed.RowParser()),
    }
    param_generator = dt_strategy.dt_param_generator_factory()
    train_start, train_end = datetime.datetime(2015, 1, 1), datetime.datetime(2015, 9, 1)
    feed_mng = feed_manager.CsvFeedManager(csv_infos)
    feed_dict = feed_mng.get_feeds_by_range(train_start, train_end)

    best_result = run_server_once(dt_strategy.DTStrategy, feed_dict, param_generator,
                                  log_key='test dt server',
                                  result_comparator=jobutil.Comparator(),
                                  batch_size=4,
                                  port=jobutil.port_dict['dt'])

    print 'best result:', best_result.getResult(), best_result.getParameters()
    result = best_result.getResult().analyze_result
    print 'all count', result.getAllCount()
    print 'net profit', result.getNetProfit()
    print 'win ratio', result.getWinRatio()
    print 'profit loss ratio', result.getProfitLossRatio()
    print 'max drawdown', result.getMaxDrawDown()
    print 'longest drawdown duration', result.getLongestDrawDownDuration()
    print 'annual return', result.getAnnualizedReturn()
    print 'sharp ratio', result.getSharpeRatio()
    result.plotEquityCurve()
    #
    # test_start = datetime.datetime(2015, 8, 1)
    # test_end = datetime.datetime(2015, 9, 1)
    # feed_dict = feed_mng.get_feeds_by_range(test_start, test_end)
    # test_result = run_strategy(dt_strategy.DTStrategy, feed_dict, result.getParameters())
    # print test_result


def test_aberration():
    import datetime
    from myalgotrade import feed
    from myalgotrade.feed import feed_manager
    from myalgotrade.strategy import Aberration

    csv_infos = {
        'l1509': (
            '../data/l1509_1min.csv', feed.Frequency.MINUTE, feed.GenericRowParser(frequency=feed.Frequency.MINUTE))
    }
    param_generator = Aberration.param_generator_factory()
    train_start, train_end = datetime.datetime(2015, 1, 1), datetime.datetime(2015, 10, 1)

    feed_mngr = feed_manager.CsvFeedManager(csv_infos)
    best_result = run_server_once(feed_mngr, train_start, train_end, param_generator, port=jobutil.port_dict['ab'])
    print 'best result', best_result.getResult(), best_result.getParameters()


def main():
    test_dt()
    # test_aberration()


if __name__ == '__main__':
    main()
