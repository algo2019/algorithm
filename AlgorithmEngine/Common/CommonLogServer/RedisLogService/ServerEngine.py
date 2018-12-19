from Common.AtTimeObjectEngine import ThreadEngine, BaseExceptionHandler


class ExceptHandler(BaseExceptionHandler):
    pk = 'RedisLogEngine'

    def process(self, engine, cmd, e):
        if hasattr(cmd, 'publish_key'):
            if cmd.publish_key == self.pk:
                return
            import traceback
            import LogMsg
            from LogCommands import LogCommand
            log_cmd = LogCommand('RedisLogEngine', 'CommonRedisLog', 'Engine', 'ERR', 'ExceptHandler',
                                 traceback.format_exc(), tuple())
            engine.add_command(LogMsg.get_msg(cmd.monitor_server,
                                              {'channel': '{}.{}.{}'.format(self.pk, self.pk, self.pk),
                                               'data': log_cmd.publish_msg}))

Engine = ThreadEngine('RedisLogService')
Engine.set_running_exception_handler(ExceptHandler())
Engine.start()
