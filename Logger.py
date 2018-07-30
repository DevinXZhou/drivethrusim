import logging

class Logger:
    def __init__(self, log_file, formatter, level = logging.INFO):
        self.form = None
        self.name = 'UNDEFINED'
        if formatter == 'msg':
            self.form = logging.Formatter('%(message)s')
            self.name = 'Drive Through Infor'
        else:
            self.form = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            self.name = 'Error Report'
            
        self.handler = logging.FileHandler(log_file)
        self.handler.setFormatter(self.form)
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(level)
        self.logger.addHandler(self.handler)
    


def main():
    log = Logger('./log/test.log', 'msg').logger

    log.info('dsfsdf')

    log.error('yoyoyo')

    
if __name__ == '__main__':
    main()
